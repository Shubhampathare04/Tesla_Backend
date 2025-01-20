from fastapi import FastAPI, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from fastapi.middleware.cors import CORSMiddleware
from models import Course
from database import courses_collection
from models import Enquiry
from database import enquiries_collection
from database import admissions_collection
from models import Admission


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

# Create a new course
@app.post("/course/", response_model=Course)
async def create_course(new_course: Course):
    course_data = new_course.dict()
    existing_course = await courses_collection.find_one({"title": course_data["title"]})
    if existing_course:
        raise HTTPException(status_code=400, detail="Course with this title already exists")
    result = await courses_collection.insert_one(course_data)
    course_data["_id"] = str(result.inserted_id)
    return bson_to_json(course_data)

# Get all courses
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

# Delete a course by ID
@app.delete("/courses/{course_id}")
async def delete_course(course_id: str):
    try:
        result = await courses_collection.delete_one({"_id": ObjectId(course_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Course not found")
        return {"message": "Course deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Course ID format")


# Update a course by ID
@app.put("/courses/{course_id}", response_model=Course)
async def update_course(course_id: str, updated_course: Course):
    try:
        # Convert updated course to dictionary
        course_data = updated_course.dict()
        # Check if the course exists
        existing_course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Update the course in the database
        result = await courses_collection.update_one(
            {"_id": ObjectId(course_id)}, {"$set": course_data}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update the course")
        
        # Return the updated course
        course_data["_id"] = course_id
        return bson_to_json(course_data)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Course ID format")


@app.post("/enquiry/")
async def create_enquiry(new_enquiry: Enquiry):
    enquiry_data = new_enquiry.dict()
    result = await enquiries_collection.insert_one(enquiry_data)
    enquiry_data["_id"] = str(result.inserted_id)
    return bson_to_json(enquiry_data)

# Get all enquiries
@app.get("/enquiries/")
async def get_all_enquiries():
    enquiries_cursor = enquiries_collection.find()
    enquiries = await enquiries_cursor.to_list(length=None)
    return [bson_to_json(enquiry) for enquiry in enquiries]

# Delete an enquiry by ID
@app.delete("/enquiries/{enquiry_id}")
async def delete_enquiry(enquiry_id: str):
    try:
        result = await enquiries_collection.delete_one({"_id": ObjectId(enquiry_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Enquiry not found")
        return {"message": "Enquiry deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Enquiry ID format")




# Create a new admissions
@app.post("/admissions/")
async def create_admission(new_admission: Admission):
    admission_data = new_admission.dict()
    try:
        result = await admissions_collection.insert_one(admission_data)
        admission_data["_id"] = str(result.inserted_id)
        return bson_to_json(admission_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create admission: {str(e)}")


# Get all admissions
@app.get("/admissions/")
async def get_all_admissions():
    admissions_cursor = admissions_collection.find()
    admissions = await admissions_cursor.to_list(length=None)
    return [bson_to_json(admission) for admission in admissions]

# Delete an admission by ID
@app.delete("/admissions/{admission_id}")
async def delete_admission(admission_id: str):
    try:
        result = await admissions_collection.delete_one({"_id": ObjectId(admission_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Admission not found")
        return {"message": "Admission deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Admission ID format")

# Update an admission by ID
@app.put("/admissions/{admission_id}", response_model=Admission)
async def update_admission(admission_id: str, updated_admission: Admission):
    try:
        # Convert updated admission to dictionary
        admission_data = updated_admission.dict()
        # Check if the admission exists
        existing_admission = await admissions_collection.find_one({"_id": ObjectId(admission_id)})
        if not existing_admission:
            raise HTTPException(status_code=404, detail="Admission not found")
        
        # Update the admission in the database
        result = await admissions_collection.update_one(
            {"_id": ObjectId(admission_id)}, {"$set": admission_data}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update the admission")
        
        # Return the updated admission
        admission_data["_id"] = admission_id
        return bson_to_json(admission_data)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Admission ID format")
