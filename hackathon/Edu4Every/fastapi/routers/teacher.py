from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel


# Pydantic model for teacher login data
class Teacher(BaseModel):
    teacher_id: str
    password: str


teacher_router = APIRouter()

# Database connection details
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Utility function to check credentials
def check_credentials(user_type: str, unique_id: str, password: str):
    with SessionLocal() as session:
        if user_type == "teacher":
            query = text("SELECT * FROM teacher WHERE teacher_id = :id AND password = :password")
            result = session.execute(query, {"id": unique_id, "password": password}).fetchone()
            return result is not None
        return False


@teacher_router.post("/login")
async def teacher_login(teacher: Teacher):
    # Check if credentials are correct
    if check_credentials("teacher", teacher.teacher_id, teacher.password):
        with SessionLocal() as session:
            # Fetch teacher's name if credentials are valid
            query = text("SELECT name FROM teacher WHERE teacher_id = :id")
            result = session.execute(query, {"id": teacher.teacher_id}).fetchone()
            teacher_name = result[0] if result else None

        # Return success response with teacher's name
        if teacher_name:
            return {"status": "success", "message": "Logged in successfully", "name": teacher_name}
        else:
            raise HTTPException(status_code=404, detail="Teacher not found")
    else:
        # Invalid credentials
        raise HTTPException(status_code=401, detail="Invalid credentials")
