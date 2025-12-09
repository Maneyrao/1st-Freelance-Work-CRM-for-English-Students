from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.DB_User import DB_User
from database.connection import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

ALGORITHM = "HS256"
SECRET = "J3"
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_DURATION_MIN = 60


@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(DB_User).filter(DB_User.username == form.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no fue encontrado"
        )

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es incorrecta"
        )

    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION_MIN)

    access_token = jwt.encode(
        {"sub": user.username, "exp": expiration},
        SECRET,
        algorithm=ALGORITHM
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_DURATION_MIN * 60
    }
