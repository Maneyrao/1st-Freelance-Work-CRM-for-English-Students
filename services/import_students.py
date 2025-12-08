import os
import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from models.DB_Student import DB_Student


def to_bool(value):
    return str(value).strip().lower() in ("true", "1", "si", "sí", "yes")


def to_int(value):
    try:
        return int(value)
    except:
        return None


def import_students_from_sheet():

    # 1️⃣ Leer variables de entorno desde Railway
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT")

    if not sheet_id or not service_account_info:
        print("Faltan variables GOOGLE_SHEET_ID o GOOGLE_SERVICE_ACCOUNT")
        return

    #Convertir JSON del service account a dict
    import json
    service_account_dict = json.loads(service_account_info)

    # Definir alcance
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    #Credenciales desde variables de entorno (no desde archivo)
    creds = Credentials.from_service_account_info(
        service_account_dict, scopes=scopes
    )

    client = gspread.authorize(creds)

    #Abrir sheet por ID (NO URL)
    sheet = client.open_by_key(sheet_id).sheet1

    #Leer datos con encabezados obligatorios
    rows = sheet.get_all_records(expected_headers=[
        "nombre",
        "telefono",
        "nivel",
        "dias_clase",
        "hora_clase",
        "cuota",
        "activo",
        "individual"
    ])

    db: Session = SessionLocal()

    for row in rows:
        nombre = row.get("nombre")
        telefono = row.get("telefono")

        if not nombre:
            continue

        existing = db.query(DB_Student).filter(
            DB_Student.nombre == nombre,
            DB_Student.telefono == telefono
        ).first()

        if existing:
            existing.nivel = row.get("nivel")
            existing.dias_clase = row.get("dias_clase")
            existing.hora_clase = row.get("hora_clase")
            existing.cuota = to_int(row.get("cuota"))
            existing.activo = to_bool(row.get("activo"))
            existing.individual = to_bool(row.get("individual"))
        else:
            new_student = DB_Student(
                nombre=nombre,
                telefono=telefono,
                nivel=row.get("nivel"),
                dias_clase=row.get("dias_clase"),
                hora_clase=row.get("hora_clase"),
                cuota=to_int(row.get("cuota")),
                activo=to_bool(row.get("activo")),
                individual=to_bool(row.get("individual")),
            )
            db.add(new_student)

    db.commit()
    db.close()

    print("Importación completa desde Google Sheets ✔")
