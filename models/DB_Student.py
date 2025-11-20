from sqlalchemy import Column, Integer, String, Boolean
from database.connection import Base

class DB_Student(Base):
    __tablename__ = "students"
    #en el día a día trabajando, va a haber celdas vacias, por eso todo es nullable=True
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=True)  
    telefono = Column(String, nullable=True)
    nivel = Column(String, nullable=True)
    dias_clase = Column(String, nullable=True)
    hora_clase = Column(String, nullable=True)
    cuota = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True, nullable=True)  
    individual = Column(Boolean, default=False, nullable=True)
