from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from models.DB_Student import DB_Student
from services.api_whatsapp_services import send_whatsapp_text
from auth.jwt_auth import current_user
    

router = APIRouter(prefix="/reminders", tags=["Reminders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# TEST
@router.post("/test")
def test_reminder(
    user = Depends(current_user)   
):
    try:
        response = send_whatsapp_text(
            "5491169004497",
            "Prueba de recordatorio desde FastAPI + WhatsApp Cloud."
        )
        return {"message": "Mensaje enviado correctamente", "response": response}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# RECORDATORIO A UN SOLO ALUMNO
@router.post("/send/{student_id}")
def send_reminder_to_student(
    student_id: int,
    db: Session = Depends(get_db),
    user = Depends(current_user)   
):
    student = db.query(DB_Student).filter(DB_Student.id == student_id).first()

    if not student:
        raise HTTPException(404, "Alumno no encontrado")

    if not student.telefono:
        raise HTTPException(400, "El alumno no tiene número de teléfono registrado")

    message = (
        f"Hola {student.nombre}, "
        f"te recordamos que tu clase está programada para {student.dias_clase} "
        f"a las {student.hora_clase}. ¡Nos vemos!"
    )

    response = send_whatsapp_text(student.telefono, message)

    return {
        "status": "OK",
        "student": student.nombre,
        "telefono": student.telefono,
        "response": response
    }


# RECORDATORIOS A TODOS LOS ACTIVOS
@router.post("/send-all-actives")
def send_reminders_to_all(
    db: Session = Depends(get_db),
    user = Depends(current_user)   
):
    students = db.query(DB_Student).filter(DB_Student.activo == True).all()

    if not students:
        return {"message": "No hay alumnos activos"}

    responses = []

    for student in students:
        if not student.telefono:
            continue

        message = (
            f"Hola {student.nombre}, este es tu recordatorio mensual de clases. "
            f"¡Gracias por estudiar con Aburridont!"
        )

        result = send_whatsapp_text(student.telefono, message)

        responses.append({
            "student": student.nombre,
            "telefono": student.telefono,
            "status": result
        })

    return {
        "message": f"Recordatorios enviados a {len(responses)} alumnos",
        "details": responses
    }


# RECORDATORIOS DE PAGO GLOBAL
@router.post("/payment-reminders")
def send_payment_reminders(
    db: Session = Depends(get_db),
    user = Depends(current_user)   
):
    students = db.query(DB_Student).filter(DB_Student.activo == True).all()

    if not students:
        return {"message": "No hay alumnos activos"}

    enviados = []
    pagados = []
    sin_telefono = []

    for student in students:

        if not student.telefono:
            sin_telefono.append(student.nombre)
            continue

        if student.pago:
            pagados.append(student.nombre)
            continue

        message = (
            f"Hola {student.nombre}, recordamos que aún no registramos el pago "
            f"de tu cuota de este mes. Si ya lo realizaste, podés ignorar este mensaje. "
            f"¡Muchas gracias! 🙌"
        )

        response = send_whatsapp_text(student.telefono, message)

        enviados.append({
            "student": student.nombre,
            "telefono": student.telefono,
            "result": response
        })

    return {
        "message": f"Recordatorios enviados a {len(enviados)} alumnos.",
        "enviados": enviados,
        "ya_pagaron": pagados,
        "sin_telefono": sin_telefono
    }
