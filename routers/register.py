from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models.DB_User import DB_User
from schemas.user import UserCreate, UserRead
from database.connection import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

crypt = CryptContext(schemes=["bcrypt"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(new_user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(DB_User).filter(DB_User.username == new_user.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso."
        )

    hashed_password = crypt.hash(new_user.password)

    user = DB_User(
        username=new_user.username,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
