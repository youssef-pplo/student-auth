from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import Student
from schemas import RegisterSchema, LoginSchema, RefreshSchema
from auth import hash_password, verify_password, create_access_token, create_refresh_token
from utils import generate_student_code, send_verification_email
import requests

app = FastAPI()

origins = ["*"]  # Allow all for now

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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

    exists = db.query(Student).filter((Student.phone == data.phone) | (Student.email == data.email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Phone or Email already registered")

    student_code = generate_student_code()

    new_student = Student(
        name=data.name,
        phone=data.phone,
        parent_phone=data.parent_phone,
        city=data.city,
        grade=data.grade,
        lang=data.lang,
        password=hash_password(data.password),
        student_code=student_code,
        email=data.email,
        is_verified=False
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # Send OTP Email
    try:
        requests.post(
            "https://easybio-drabdelrahman.com/otp-system/send.php",
            data={"email": new_student.email}
        )
    except:
        pass

    return {
        "status": "success",
        "message": "Registered. Please check your email to verify."
    }


@app.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    student = db.query(Student).filter(
        (Student.phone == data.identifier) |
        (Student.student_code == data.identifier) |
        (Student.email == data.identifier)
    ).first()

    if not student or not verify_password(data.password, student.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not student.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = create_access_token({"sub": student.phone})
    refresh_token = create_refresh_token({"sub": student.phone})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "student": {
            "name": student.name,
            "student_code": student.student_code,
            "phone": student.phone,
            "email": student.email,
            "lang": student.lang
        }
    }


@app.post("/token/refresh")
def refresh_token(data: RefreshSchema):
    refresh_token = data.refresh_token
    # TODO: add validation if needed
    new_token = create_access_token({"sub": "student"})
    return {"access_token": new_token}
