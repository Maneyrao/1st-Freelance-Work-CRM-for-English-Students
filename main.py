from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import students, reminder

app = FastAPI(title="TEST-ABURRIDONT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"msg": "API funcionando", "cors": True}

app.include_router(students.router)
app.include_router(reminder.router)
