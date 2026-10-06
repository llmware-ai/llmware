from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel


# Pydantic model for student login data
class Student(BaseModel):
    unique_id: str
    password: str


student_router = APIRouter()

# Database connection details
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Utility function to check credentials
def check_credentials(user_type: str, unique_id: str, password: str):
    with SessionLocal() as session:
        if user_type == "student":
            query = text("SELECT * FROM student WHERE unique_id = :id AND password = :password")
            result = session.execute(query, {"id": unique_id, "password": password}).fetchone()
            return result is not None
        return False


@student_router.post("/login")
async def student_login(student: Student):
    # Check if credentials are correct
    if check_credentials("student", student.unique_id, student.password):
        with SessionLocal() as session:
            # Fetch student's name if credentials are valid
            query = text("SELECT name FROM student WHERE unique_id = :id")
            result = session.execute(query, {"id": student.unique_id}).fetchone()
            student_name = result[0] if result else None

        # Return success response with student's name
        if student_name:
            return {"status": "success", "message": "Logged in successfully", "name": student_name}
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    else:
        # Invalid credentials
        raise HTTPException(status_code=401, detail="Invalid credentials")
