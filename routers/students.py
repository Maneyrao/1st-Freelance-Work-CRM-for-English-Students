from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.DB_Student import DB_Student
from database.connection import SessionLocal
  #Modelo BD
from schemas.Student import StudentRead, StudentCreate
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
    db: Session = Depends(get_db)
):
    query = db.query(DB_Student)

    if individual is not None:
        query = query.filter(DB_Student.individual == individual)

    if activo is not None:
        query = query.filter(DB_Student.activo == activo)
    return query.all()

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


@router.post("/sync")
def sync_students():
    import_students_from_sheet()
    return {"message": "Sincronización completa"}

