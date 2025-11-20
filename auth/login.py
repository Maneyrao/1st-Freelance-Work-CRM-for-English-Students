from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.DB_Student import User
from database.connection import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

ALGORITHM = "HS256"

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


crypt = CryptContext(schemes=["bcrypt"])


acces_token_duration = 10
SECRET = "J3"
exception400= status.HTTP_400_BAD_REQUEST

@router.post("/login")

async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user:
        raise HTTPException(
           status_code = exception400,detail="el usuario no se ha encontrado" ) 
        

    
    
    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code = exception400, detail="la contraseña no coincide")
        

    acces_token_expiration = timedelta(minutes=acces_token_duration)
    
    acces_token = jwt.encode(
    {"sub": user.username, "exp": datetime.utcnow() + timedelta(minutes=acces_token_duration)},
    SECRET,
    algorithm=ALGORITHM
    )

    return {"access_token": acces_token, "token_type": "bearer"}

