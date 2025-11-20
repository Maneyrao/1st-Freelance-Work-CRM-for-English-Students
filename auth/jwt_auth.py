from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from schemas.Student import UserRead
from models.DB_Student import User as DBUser
from auth.login import SECRET, ALGORITHM, oauth2
from database.connection import get_db



#excepciones
exception401 = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas", 
            headers={"WWW-Authenticate": "Bearer"})

exception404 = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Usuario no encontrado"
)
async def auth_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")  
        if username is None:
            raise exception401
    except JWTError:
        raise exception401

    
    user = db.query(DBUser).filter(DBUser.username == username).first()

    if not user:  #se verifica
        raise exception404

    return user



async def current_user(user: DBUser = Depends(auth_user)):
    return user
