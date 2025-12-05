from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.DB_Student import DB_Student
from database.connection import SessionLocal
  #Modelo BD
from schemas.Student import StudentRead, StudentCreate, StudentUpdate
from fastapi import status, HTTPException
from services.import_students import import_students_from_sheet


not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado")

router = APIRouter(prefix="/students", tags=["Students"])
#conexión a la base de datos de sql
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/", response_model=StudentRead)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = DB_Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student



#manera súper dinámica de filtrar
#en la ruta hay que poner ?individual=True (para que devuelva los ind)
                          #?activo=True (para que devuelva los activos)

@router.get("/", response_model=list[StudentRead])
def get_students(
    individual: bool | None = None,
    activo: bool | None = None,
    id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(DB_Student)

    if id is not None:
        query = query.filter(DB_Student.id == id)

    if individual is not None:
        query = query.filter(DB_Student.individual == individual)

    if activo is not None:
        query = query.filter(DB_Student.activo == activo)

    return query.order_by(DB_Student.id).all()



@router.patch("/{student_id}/desactivar", response_model=StudentRead)
def desactivar_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(DB_Student).filter(DB_Student.id == student_id).first()
    
    if not student:
        raise not_found
    
    student.activo = False
    db.commit()
    db.refresh(student)

    return student

@router.patch("/{student_id}/activar", response_model=StudentRead)
def activar_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(DB_Student).filter(DB_Student.id == student_id).first()
    
    if not student:
        raise not_found
    
    student.activo = True
    db.commit()
    db.refresh(student)

    return student
#NO ESTÁ TESTEADO AÚN

#ACTIVAR/DESACTIVAR EL PAGO DE CADA ALUMNO (En base a si pagó o no.)
#PATCH http://127.0.0.1:8000/students/3/pago?estado=true/false (en base a si debe o NO.)

@router.patch("/{id}/pago", response_model=StudentRead)
def actualizar_pago(
    id: int,
    estado: bool,
    db: Session = Depends(get_db),
):
    # 1. Buscar al alumno
    student = db.query(DB_Student).filter(DB_Student.id == id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    if estado not in [True, False]:
        raise HTTPException(
            status_code=400,
            detail="El parámetro 'estado' debe ser true o false."
        )
    student.pago = estado
    db.commit()
    db.refresh(student)
    return student

#sincronizar los datos de Google Sheets para importarlos a la base de datos.
@router.post("/sync", status_code=200)
def sync_students(db: Session = Depends(get_db)):
    try:
        resultado = import_students_from_sheet()
        return {"status": "ok", "message": "Sincronización completa", "detalles": resultado}
    
    except FileNotFoundError:
        #Credenciales o archivo no encontrado
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo de credenciales o el archivo de Google Sheets.")
        
@router.get("/recaudacion")
def obtener_recaudacion(db: Session = Depends(get_db)):
    # Filtrar SOLO activos
    students = db.query(DB_Student).filter(DB_Student.activo == True).all()

    # Totales
    total_pagado = sum((a.cuota or 0) for a in students if a.pago)
    total_pendiente = sum((a.cuota or 0) for a in students if not a.pago)
    cantidad_pagaron = sum(1 for a in students if a.pago)
    cantidad_pendientes = sum(1 for a in students if not a.pago)

    # Listas detalladas
    pagaron = [
        {
            "id": a.id,
            "nombre": a.nombre,
            "cuota": a.cuota,
            "telefono": a.telefono,
        }
        for a in students if a.pago
    ]

    deben = [
        {
            "id": a.id,
            "nombre": a.nombre,
            "cuota": a.cuota,
            "telefono": a.telefono,
        }
        for a in students if not a.pago
    ]

    return {
        "total_pagado": total_pagado,
        "total_pendiente": total_pendiente,
        "cantidad_pagaron": cantidad_pagaron,
        "cantidad_pendientes": cantidad_pendientes,
        "pagaron": pagaron,
        "deben": deben,
    }

@router.patch("/{student_id}", response_model=StudentRead)
def actualizar_alumno(student_id: int, info: StudentUpdate, db: Session = Depends(get_db)):

    student = db.query(DB_Student).filter(DB_Student.id == student_id).first()
    if not student:
        raise HTTPException(404, "Alumno no encontrado")

    # Actualizar solo los campos que mandó el frontend
    update_data = info.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return student
