from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel


# Pydantic model for carrier guidance login data
class CarrierGuidance(BaseModel):
    unique_id: str
    password: str


carrier_guidance_router = APIRouter()

# Database connection details
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Utility function to check credentials
def check_credentials(user_type: str, unique_id: str, password: str):
    with SessionLocal() as session:
        if user_type == "carrier_guidance":
            query = text("SELECT * FROM carrier_guidance WHERE unique_id = :id AND password = :password")
            result = session.execute(query, {"id": unique_id, "password": password}).fetchone()
            return result is not None
        return False


@carrier_guidance_router.post("/login")
async def carrier_guidance_login(credentials: CarrierGuidance):
    # Check if credentials are correct
    if check_credentials("carrier_guidance", credentials.unique_id, credentials.password):
        with SessionLocal() as session:
            # Fetch carrier guidance's name if credentials are valid
            query = text("SELECT name FROM carrier_guidance WHERE unique_id = :id")
            result = session.execute(query, {"id": credentials.unique_id}).fetchone()
            carrier_guidance_name = result[0] if result else None

        # Return success response with carrier guidance's name
        if carrier_guidance_name:
            print("Name: ", carrier_guidance_name)
            return {"status": "success", "message": "Logged in successfully", "name": carrier_guidance_name}
        else:
            raise HTTPException(status_code=404, detail="Carrier guidance not found")
    else:
        # Invalid credentials
        raise HTTPException(status_code=401, detail="Invalid credentials")