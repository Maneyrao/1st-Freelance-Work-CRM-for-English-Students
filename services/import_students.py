import os
import json
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

    # 1) Leer variables de entorno desde Railway
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT")

    if not sheet_id or not service_account_info:
        print(" Faltan GOOGLE_SHEET_ID o GOOGLE_SERVICE_ACCOUNT")
        return

    try:
        # Convertir JSON del service account en dict
        # Railway a veces agrega \n escapados, esto lo corrige
        service_account_dict = json.loads(service_account_info)
    except Exception as e:
        print("Error parseando GOOGLE_SERVICE_ACCOUNT:", e)
        return

    # 2) Definir alcance
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    # 3) Credenciales desde variables de entorno
    creds = Credentials.from_service_account_info(
        service_account_dict,
        scopes=scopes
    )

    # 4) Autorización
    client = gspread.authorize(creds)

    # 5) Abrir sheet por ID (NO URL)
    sheet = client.open_by_key(sheet_id).sheet1

    # 6) Leer registros
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
            continue  # fila vacía

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

    print("✔ Importación completa desde Google Sheets")
