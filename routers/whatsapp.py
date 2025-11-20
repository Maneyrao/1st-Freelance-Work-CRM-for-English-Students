from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from models.DB_Student import DB_Student
from services.api_whatsapp_services import send_whatsapp_template

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1) ENVIAR RECORDATORIO DE PAGO POR ID
@router.post("/pago/{student_id}")
def enviar_recordatorio_pago(student_id: int, db: Session = Depends(get_db)):

    alumno = db.query(DB_Student).filter(DB_Student.id == student_id).first()

    if not alumno:
        raise HTTPException(404, "Alumno no encontrado")

    if not alumno.telefono:
        raise HTTPException(400, "El alumno no tiene teléfono registrado")

    variables = [
        alumno.nombre,
        "1 al 10",          # {{2}} – período (puede ser dinámico)
        str(alumno.cuota),  # {{3}} – monto
    ]

    return send_whatsapp_template(
        to_number=alumno.telefono,
        template_name="pago_pendiente_mensualidad",
        variables=variables
    )


# ENVIAR MENSAJE DE BIENVENIDA
@router.post("/bienvenida/{student_id}")
def enviar_bienvenida(student_id: int, db: Session = Depends(get_db)):

    alumno = db.query(DB_Student).filter(DB_Student.id == student_id).first()

    if not alumno:
        raise HTTPException(404, "Alumno no encontrado")

    if not alumno.telefono:
        raise HTTPException(400, "El alumno no tiene teléfono registrado")

    variables = [
        alumno.nombre,           # {{1}}
        "12 de marzo",           # {{2}} – fecha de inicio (dinámico si querés)
        alumno.dias_clase or "", # {{3}}
        alumno.hora_clase or "", # {{4}}
    ]

    return send_whatsapp_template(
        to_number=alumno.telefono,
        template_name="bienvenida_inicio_curso",
        variables=variables
    )
    
from services.api_whatsapp_services import send_whatsapp_template, send_whatsapp_text
import time


@router.post("/pago/doble/{student_id}")
def enviar_recordatorio_pago_completo(student_id: int, db: Session = Depends(get_db)):

    alumno = db.query(DB_Student).filter(DB_Student.id == student_id).first()

    if not alumno:
        raise HTTPException(404, "Alumno no encontrado")

    if not alumno.telefono:
        raise HTTPException(400, "El alumno no tiene teléfono registrado")


    # 1) VARIABLES PARA LA PLANTILLA
    variables = [
        alumno.nombre,
        "1 al 10", 
        str(alumno.cuota or 0)
    ]

    # 2) ENVIAR PLANTILLA
    plantilla_response = send_whatsapp_template(
        to_number=alumno.telefono,
        template_name="pago_pendiente_mensualidad",
        variables=variables
    )

    # 3) ESPERAR 1 SEGUNDO
    time.sleep(1)

    # 4) MENSAJE LIBRE POST PLANTILLA
    mensaje_extra = f"""
Alias: tmaneyro.nx
CBU: 4530000800014889546168
Monto: ${alumno.cuota}

¿Necesitás factura?
Cuando realices el pago, enviame el comprobante.
"""

    msg_response = send_whatsapp_text(
        to_number=alumno.telefono,
        message=mensaje_extra
    )

    return {
        "plantilla": plantilla_response,
        "mensaje_extra": msg_response
    }
