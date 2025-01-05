from pydantic import BaseModel
from typing import Optional
from bson import ObjectId  # Import ObjectId

# Schema for incoming requests
class TeamMember(BaseModel):
    id: int
    name: str
    role: str
    photo: Optional[str] = None

    class Config:
        # Allow MongoDB's ObjectId to be used as a string
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string
        }

# Schema for database objects
class TeamMemberInDB(TeamMember):
    _id: str


# Schema for courses
class Course(BaseModel):
    title: str
    description: str
    courselink: str
    standard: str

    class Config:
        # Allow MongoDB's ObjectId to be used as a string
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string
        }


class Enquiry(BaseModel):
    name: str
    class_name: str  # Use 'class_name' instead of 'class' to avoid Python keyword conflict
    board: str
    subject: str
    country: str
    phone: str
    enquiryMessage: str

    class Config:
        # Allow MongoDB's ObjectId to be used as a string
        json_encoders = {
            ObjectId: str
        }
