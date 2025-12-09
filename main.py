from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.login import router as auth_router
from routers.students import router as students_router
from routers.reminder import router as reminder_router
from routers.whatsapp import router as whatsapp_router
from routers.register import router as register_router

from database.connection import Base, engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(reminder_router)
app.include_router(whatsapp_router)
app.include_router(register_router)
