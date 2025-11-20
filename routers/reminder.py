from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from models.DB_Student import DB_Student
from services.whatsapp_msg_reminder import send_whatsapp_message

router = APIRouter(prefix="/reminders", tags=["Reminders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/test")
def test_reminder():

    #Envía un mensaje de prueba a un número determinado para verificar la conexión con WhatsApp Cloud 
    try:
        #Cambiá el número a tu WhatsApp (sin el +, ej: 5491169004497)
        response = send_whatsapp_message("5491169004497", "Prueba de recordatorio desde FastAPI + WhatsApp Cloud.")
        return {"message": "Mensaje enviado correctamente", "response": response}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    

@router.post("/send/{student_id}") #solo a un alumno.
def send_reminder_to_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(DB_Student).filter(DB_Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    if not student.telefono:
        raise HTTPException(status_code=400, detail="El alumno no tiene número de teléfono registrado")

    message = f"Hola {student.nombre}, te recordamos que tu clase está programada para {student.dias_clase} a las {student.hora_clase}. ¡Nos vemos!"
    
    response = send_whatsapp_message(student.telefono, message)

    return {
        "status": "OK",
        "student": student.nombre,
        "telefono": student.telefono,
        "response": response
    }
    
    
    
    


@router.post("/send-all-actives") #####SEND MESSAGE A TODOS LOS ALUMNOS, HAY QUE CAMBIAR.
def send_reminders_to_all(db: Session = Depends(get_db)):
    students = db.query(DB_Student).filter(DB_Student.activo == True).all()

    if not students:
        return {"message": "No hay alumnos activos"}

    responses = []

    for student in students:
        if not student.telefono:
            continue

        message = f"Hola {student.nombre}, este es tu recordatorio mensual de clases. ¡Gracias por estudiar con Aburridont!"
        result = send_whatsapp_message(student.telefono, message)
        responses.append({
            "student": student.nombre,
            "telefono": student.telefono,
            "status": result
        })

    return {
        "message": f"Recordatorios enviados a {len(responses)} alumnos",
        "details": responses
    }


@router.post("/payment-reminders")
def send_payment_reminders(db: Session = Depends(get_db)):
    """
    Envía recordatorios de pago a los alumnos activos que NO pagaron todavía.
    Usado para los días 1, 5 y 10 de cada mes (cron job futuro).
    """
    students = db.query(DB_Student).filter(DB_Student.activo == True).all()

    if not students:
        return {"message": "No hay alumnos activos"}

    enviados = []
    pagados = []
    sin_telefono = []

    for student in students:

        # Si no tiene teléfono → no se puede mandar
        if not student.telefono:
            sin_telefono.append(student.nombre)
            continue

        # Si ya pagó → no mandamos recordatorio
        if student.pago:
            pagados.append(student.nombre)
            continue

        # Si no pagó → mandamos recordatorio
        message = (
            f"Hola {student.nombre}, "
            f"recordamos que aún no registramos el pago de tu cuota de este mes. "
            f"Si ya lo realizaste, podés ignorar este mensaje. ¡Muchas gracias! 🙌"
        )

        response = send_whatsapp_message(student.telefono, message)

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


