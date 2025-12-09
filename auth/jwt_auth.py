from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from schemas.user import UserRead
from models.DB_User import DB_User
from auth.login import SECRET, ALGORITHM, oauth2
from database.connection import get_db



#excepciones
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
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
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

    #busca al usuario
    user = db.query(DB_User).filter(DB_User.username == username).first()

    if not user:  #se verifica
        raise exception404

    return UserRead.model_validate(user)



async def current_user(user: UserRead = Depends(auth_user)):
    return user