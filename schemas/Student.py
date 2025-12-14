from pydantic import BaseModel
from typing import Optional

#base del student, sin ID, porque lo genera autoincrementadamente SQL
#es la que se usa para CRUD
class StudentBase(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    nivel: Optional[str] = None
    dias_clase: Optional[str] = None
    hora_clase: Optional[str] = None
    cuota: Optional[int] = None
    activo: Optional[bool] = True
    individual: Optional[bool] = False
    pago: Optional[bool] = False
#pass porque es lo estandar de fastapi, se usa para los post en la api.
class StudentCreate(StudentBase):
    pass

#al student, se le suma el id que aplicamos acá, está separado
class StudentRead(StudentBase):
    id: int
    class Config:
        orm_mode = True



class StudentUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    nivel: Optional[str] = None
    dias_clase: Optional[str] = None
    hora_clase: Optional[str] = None
    cuota: Optional[int] = None
    activo: Optional[bool] = None
    individual: Optional[bool] = None
    pago: Optional[bool] = None
    
    
    