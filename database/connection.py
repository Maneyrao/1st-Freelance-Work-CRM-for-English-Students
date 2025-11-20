from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./students.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()

Base = declarative_base() 



def init_db():
    from models import DB_Student  # importa los modelos para registrarlos
    Base.metadata.create_all(bind=engine)
    
#Dependencia para usar en Depends
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
