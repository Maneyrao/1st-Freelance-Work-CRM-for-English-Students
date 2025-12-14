import os
import json
import base64
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


def normalize_str(value):
    if value is None:
        return None
    return str(value).strip()


def load_google_credentials():
    is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT"))

    if is_railway:
        raw_b64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_B64")
        if not raw_b64:
            raise RuntimeError(
                "Railway detectado pero GOOGLE_SERVICE_ACCOUNT_B64 no está definido"
            )

        try:
            decoded = base64.b64decode(raw_b64).decode("utf-8")
            return json.loads(decoded)
        except Exception as e:
            raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_B64 inválido") from e

    service_account_path = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_PATH",
        "service_account.json"
    )

    if not os.path.exists(service_account_path):
        raise RuntimeError(
            f"No se encuentra {service_account_path} (modo local)"
        )

    with open(service_account_path, "r", encoding="utf-8") as f:
        return json.load(f)


def import_students_from_sheet():
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise RuntimeError("Falta GOOGLE_SHEET_ID")

    service_account_dict = load_google_credentials()

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
            nombre = normalize_str(row.get("nombre"))
            telefono = normalize_str(row.get("telefono"))

            if not nombre or not telefono:
                continue

            existing = db.query(DB_Student).filter(
                DB_Student.nombre == nombre,
                DB_Student.telefono == telefono
            ).first()

            if existing:
                existing.nivel = normalize_str(row.get("nivel"))
                existing.dias_clase = normalize_str(row.get("dias_clase"))
                existing.hora_clase = normalize_str(row.get("hora_clase"))
                existing.cuota = to_int(row.get("cuota"))
                existing.activo = to_bool(row.get("activo"))
                existing.individual = to_bool(row.get("individual"))
            else:
                db.add(DB_Student(
                    nombre=nombre,
                    telefono=telefono,
                    nivel=normalize_str(row.get("nivel")),
                    dias_clase=normalize_str(row.get("dias_clase")),
                    hora_clase=normalize_str(row.get("hora_clase")),
                    cuota=to_int(row.get("cuota")),
                    activo=to_bool(row.get("activo")),
                    individual=to_bool(row.get("individual")),
                ))

        db.commit()

    finally:
        db.close()

    return {
        "status": "ok",
        "imported": len(rows)
    }


if __name__ == "__main__":
    import_students_from_sheet()
