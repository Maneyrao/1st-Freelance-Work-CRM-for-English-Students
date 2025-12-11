from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import Base, engine

# IMPORTAR MODELOS ANTES DEL CREATE_ALL
from models.DB_Student import DB_Student
from models.DB_User import DB_User

# Crear tablas
Base.metadata.create_all(bind=engine)

# Importar routers DESPUÉS (para evitar circulares)
from auth.login import router as auth_router
from auth.register import router as register_router
from routers.students import router as students_router
from routers.reminder import router as reminder_router
from routers.whatsapp import router as whatsapp_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(register_router)
app.include_router(students_router)
app.include_router(reminder_router)
app.include_router(whatsapp_router)
