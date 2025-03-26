from fastapi import FastAPI, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from fastapi.middleware.cors import CORSMiddleware
from models import Course, Enquiry, Admission, Progress
from database import courses_collection, enquiries_collection, admissions_collection, progress_collection
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to convert BSON to JSON-friendly format
def bson_to_json(data):
    data["_id"] = str(data["_id"])
    return data

# Course model (already updated as per your input)
class Course(BaseModel):
    title: str
    description: str
    courselink: str
    standard: str

    class Config:
        json_encoders = {ObjectId: str}

# Progress model (unchanged, but included for clarity)
class Progress(BaseModel):
    user_id: str
    course_title: str
    completed: bool = False
    # No link field here; we'll fetch it from courses_collection

# Completion update model
class CompletionUpdate(BaseModel):
    completed: bool

# Existing endpoints (abbreviated)
@app.post("/course/", response_model=Course)
async def create_course(new_course: Course):
    course_data = new_course.dict()
    existing_course = await courses_collection.find_one({"title": course_data["title"]})
    if existing_course:
        raise HTTPException(status_code=400, detail="Course with this title already exists")
    result = await courses_collection.insert_one(course_data)
    course_data["_id"] = str(result.inserted_id)
    return bson_to_json(course_data)

@app.get("/courses/")
async def get_all_courses():
    courses_cursor = courses_collection.find()
    courses = await courses_cursor.to_list(length=None)
    grouped_courses = {}
    for course in courses:
        standard = course.get("standard", "Others")
        if standard not in grouped_courses:
            grouped_courses[standard] = []
        grouped_courses[standard].append(bson_to_json(course))
    return grouped_courses

@app.post("/buy_course/", response_model=Progress)
async def buy_course(purchase: Progress):
    try:
        course = await courses_collection.find_one({"title": purchase.course_title})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        existing_progress = await progress_collection.find_one({
            "user_id": purchase.user_id,
            "course_title": purchase.course_title
        })
        if existing_progress:
            raise HTTPException(status_code=400, detail="You have already purchased this course")
        
        progress_data = purchase.dict()
        result = await progress_collection.insert_one(progress_data)
        progress_data["_id"] = str(result.inserted_id)
        return bson_to_json(progress_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error purchasing course: {str(e)}")

# Updated endpoint to include courselink
@app.get("/progress/{user_id}")
async def get_user_progress(user_id: str):
    try:
        progress_cursor = progress_collection.find({"user_id": user_id})
        progress_list = await progress_cursor.to_list(length=None)
        if not progress_list:
            return []

        # Fetch corresponding course data to get courselink
        enriched_progress = []
        for progress in progress_list:
            course = await courses_collection.find_one({"title": progress["course_title"]})
            progress_data = bson_to_json(progress)
            if course:
                progress_data["courselink"] = course.get("courselink", "")
            else:
                progress_data["courselink"] = ""  # Fallback if course not found
            enriched_progress.append(progress_data)

        return enriched_progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress: {str(e)}")

@app.put("/complete_course/{progress_id}", response_model=Progress)
async def complete_course(progress_id: str, update: CompletionUpdate):
    try:
        progress = await progress_collection.find_one({"_id": ObjectId(progress_id)})
        if not progress:
            raise HTTPException(status_code=404, detail="Course progress not found")

        result = await progress_collection.update_one(
            {"_id": ObjectId(progress_id)},
            {"$set": {"completed": update.completed}}
        )

        updated_progress = await progress_collection.find_one({"_id": ObjectId(progress_id)})
        return bson_to_json(updated_progress)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Progress ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating course completion: {str(e)}")

@app.post("/buy_course/", response_model=Progress)
async def buy_course(purchase: Progress):
    try:
        if not await courses_collection.find_one({"title": purchase.course_title}):
            raise HTTPException(status_code=404, detail="Course not found")

        if await progress_collection.find_one({"user_id": purchase.user_id, "course_title": purchase.course_title}):
            raise HTTPException(status_code=400, detail="Course already purchased")

        progress_data = purchase.dict()
        result = await progress_collection.insert_one(progress_data)
        progress_data["_id"] = str(result.inserted_id)
        return bson_to_json(progress_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error purchasing course: {str(e)}")

@app.get("/progress/{user_id}")
async def get_user_progress(user_id: str):
    try:
        progress = await progress_collection.find({"user_id": user_id}).to_list(length=None)
        return [bson_to_json(item) for item in progress]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress: {str(e)}")

### ENQUIRY ROUTES ###

@app.post("/enquiry/")
async def create_enquiry(new_enquiry: Enquiry):
    enquiry_data = new_enquiry.dict()
    result = await enquiries_collection.insert_one(enquiry_data)
    enquiry_data["_id"] = str(result.inserted_id)
    return bson_to_json(enquiry_data)

@app.get("/enquiries/")
async def get_all_enquiries():
    enquiries = await enquiries_collection.find().to_list(length=None)
    return [bson_to_json(enquiry) for enquiry in enquiries]

@app.delete("/enquiries/{enquiry_id}")
async def delete_enquiry(enquiry_id: str):
    try:
        result = await enquiries_collection.delete_one({"_id": ObjectId(enquiry_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Enquiry not found")
        return {"message": "Enquiry deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Enquiry ID format")

### ADMISSION ROUTES ###

@app.post("/admissions/")
async def create_admission(new_admission: Admission):
    try:
        admission_data = new_admission.dict()
        result = await admissions_collection.insert_one(admission_data)
        admission_data["_id"] = str(result.inserted_id)
        return bson_to_json(admission_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create admission: {str(e)}")

@app.get("/admissions/")
async def get_all_admissions():
    admissions = await admissions_collection.find().to_list(length=None)
    return [bson_to_json(admission) for admission in admissions]

@app.delete("/admissions/{admission_id}")
async def delete_admission(admission_id: str):
    try:
        result = await admissions_collection.delete_one({"_id": ObjectId(admission_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Admission not found")
        return {"message": "Admission deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Admission ID format")

@app.put("/admissions/{admission_id}", response_model=Admission)
async def update_admission(admission_id: str, updated_admission: Admission):
    try:
        admission_data = updated_admission.dict()
        if not await admissions_collection.find_one({"_id": ObjectId(admission_id)}):
            raise HTTPException(status_code=404, detail="Admission not found")

        result = await admissions_collection.update_one(
            {"_id": ObjectId(admission_id)}, {"$set": admission_data}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update the admission")

        admission_data["_id"] = admission_id
        return bson_to_json(admission_data)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Admission ID format")
