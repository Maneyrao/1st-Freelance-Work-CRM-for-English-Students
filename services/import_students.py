import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from models.DB_Student import DB_Student

sheet_url = "https://docs.google.com/spreadsheets/d/1oI7fAMAJT61EPPvdzqz-TvCdNOVNcp75hfSvnmz3n6Q/edit?usp=sharing"

def to_bool(value):
    return str(value).strip().lower() in ("true", "1", "si", "sí", "yes")

def to_int(value):
    try:
        return int(value)
    except:
        return None

def import_students_from_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(sheet_url).sheet1

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

        # Se identifica alumno por nombre + teléfono
        existing = db.query(DB_Student).filter(
            DB_Student.nombre == nombre,
            DB_Student.telefono == telefono
        ).first()

        if existing:
            #si existe, se actualiza.
            existing.nivel = row.get("nivel")
            existing.dias_clase = row.get("dias_clase")
            existing.hora_clase = row.get("hora_clase")
            existing.cuota = to_int(row.get("cuota"))
            existing.activo = to_bool(row.get("activo"))
            existing.individual = to_bool(row.get("individual"))
        else:
            #se crea si no existe
            student = DB_Student(
                nombre=nombre,
                telefono=telefono,
                nivel=row.get("nivel"),
                dias_clase=row.get("dias_clase"),
                hora_clase=row.get("hora_clase"),
                cuota=to_int(row.get("cuota")),
                activo=to_bool(row.get("activo")),
                individual=to_bool(row.get("individual")),
            )
            db.add(student)

    db.commit()
    db.close()

    print("Importación completa")
