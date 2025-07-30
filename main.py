from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import Student
from schemas import RegisterSchema, LoginSchema
from auth import hash_password, verify_password, create_access_token
from utils import generate_student_code

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    existing = db.query(Student).filter(Student.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")

    student_code = generate_student_code()

    new_student = Student(
        name=data.name,
        phone=data.phone,
        parent_phone=data.parent_phone,
        city=data.city,
        grade=data.grade,
        lang=data.lang,
        password=hash_password(data.password),
        student_code=student_code
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    token = create_access_token({"sub": new_student.phone})
    return {"token": token, "student": {
        "name": new_student.name,
        "student_code": new_student.student_code,
        "phone": new_student.phone,
        "lang": new_student.lang
    }}

@app.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    student = db.query(Student).filter(
        (Student.phone == data.identifier) |
        (Student.student_code == data.identifier)
    ).first()

    if not student or not verify_password(data.password, student.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": student.phone})
    return {"token": token, "student": {
        "name": student.name,
        "student_code": student.student_code,
        "phone": student.phone,
        "lang": student.lang
    }}
