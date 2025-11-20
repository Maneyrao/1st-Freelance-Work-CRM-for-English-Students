from fastapi import FastAPI
from routers import students, reminder
from database.connection import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(students.router)
app.include_router(reminder.router)
