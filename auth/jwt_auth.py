from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session
import os

from schemas.user import UserRead
from models.DB_User import DB_User
from database.connection import get_db


# =========================
# CONFIGURACIÓN DE JWT 
# =========================
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no configurada en variables de entorno.")

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

exception401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token inválido o expirado",
    headers={"WWW-Authenticate": "Bearer"}
)

exception404 = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Usuario no encontrado"
)


async def auth_user(
    token: str = Depends(oauth2),
    db: Session = Depends(get_db)
):
    """
    Valida el token JWT, verifica expiración,
    busca al usuario en la base de datos y retorna UserRead.
    """

    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise exception401

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token expiró. Inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise exception401
    user = db.query(DB_User).filter(DB_User.username == username).first()
    if not user:
        raise exception404
    return UserRead.model_validate(user)
async def current_user(user: UserRead = Depends(auth_user)):
    return user
