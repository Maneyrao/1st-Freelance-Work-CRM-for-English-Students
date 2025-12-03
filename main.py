from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import students, reminder

app = FastAPI(title="TEST-ABURRIDONT")

# CORS: permitir llamadas desde cualquier origen (después lo afinamos)
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

# Routers
app.include_router(students.router)
app.include_router(reminder.router)
