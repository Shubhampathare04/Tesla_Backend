from pydantic import BaseModel
from typing import Optional
from bson import ObjectId

# Schema for incoming requests
class TeamMember(BaseModel):
    id: int
    name: str
    role: str
    photo: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}

class TeamMemberInDB(TeamMember):
    _id: str

# Schema for courses (updated with total_lessons)
class Course(BaseModel):
    title: str
    description: str
    courselink: str
    standard: str
    price: float  # Adding price field

    class Config:
        json_encoders = {ObjectId: str}
        
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    courselink: Optional[str] = None
    standard: Optional[str] = None
    price: Optional[float] = None

    class Config:
        json_encoders = {ObjectId: str}


# Schema for progress (new)
class Progress(BaseModel):
    user_id: str
    course_title: str
    completed: bool = False
    link: Optional[str] = None 

class Enquiry(BaseModel):
    name: str
    class_name: str
    board: str
    subject: str
    country: str
    phone: str
    enquiryMessage: str

    class Config:
        json_encoders = {ObjectId: str}

class Admission(BaseModel):
    student_name: str
    course: str
    board: str
    subjects: str
    joining_date: str
    address: str
    contact_no: str
    fees: float

    class Config:
        json_encoders = {ObjectId: str}
        
