import os
import json
import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database.connection import SessionLocal
from models.DB_Student import DB_Student


def to_bool(value):
    return str(value).strip().lower() in ("true", "1", "si", "sí", "yes")


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def import_students_from_sheet():
    
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    # Path al service account (default: service_account.json)
    service_account_path = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_PATH",
        "service_account.json"
    )

    if not sheet_id:
        raise RuntimeError("Falta GOOGLE_SHEET_ID")

    if not os.path.exists(service_account_path):
        raise RuntimeError(
            f"No se encuentra el archivo de credenciales: {service_account_path}"
        )
    try:
        with open(service_account_path, "r", encoding="utf-8") as f:
            service_account_dict = json.load(f)
    except Exception as e:
        raise RuntimeError("Error leyendo service_account.json") from e


    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]


    creds = Credentials.from_service_account_info(
        service_account_dict,
        scopes=scopes
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1


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

    try:
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
                db.add(DB_Student(
                    nombre=nombre,
                    telefono=telefono,
                    nivel=row.get("nivel"),
                    dias_clase=row.get("dias_clase"),
                    hora_clase=row.get("hora_clase"),
                    cuota=to_int(row.get("cuota")),
                    activo=to_bool(row.get("activo")),
                    individual=to_bool(row.get("individual")),
                ))

        db.commit()

    finally:
        db.close()

    print(f"✔ Importación completa ({len(rows)} alumnos)")

    return {
        "status": "ok",
        "imported": len(rows)
    }


# Permite ejecución directa
if __name__ == "__main__":
    import_students_from_sheet()
