from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import students, reminder, whatsapp
from database.connection import Base, engine

app = FastAPI(
    title="Aburridont API",
    version="1.0.0"
)

# CORS CONFIG (mejor cerrada)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción usar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Routers principales
app.include_router(students.router)
app.include_router(reminder.router)
app.include_router(whatsapp.router)

# (Opcional) Eliminar router de pruebas
# app.include_router(test_plantilla.router)
