from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import students, reminder, whatsapp
from database.connection import Base, engine

app = FastAPI(
    title="Aburridont API",
    version="1.0.0"
)

# CORS CONFIG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(students.router)
app.include_router(reminder.router)
app.include_router(whatsapp.router)

# Ruta raíz
@app.get("/")
def root():
    return {"msg": "API funcionando", "cors": True}
