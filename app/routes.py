from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from urllib.parse import quote_plus
import urllib.parse
import json
from fastapi import FastAPI, Query
from fastapi import FastAPI, Body
from statistics import mean, median, stdev
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import numpy as np
import nltk
nltk.download('vader_lexicon')
from fastapi import Form
from datetime import datetime, timedelta
from db import collection, collection_1, collection_2,collection_3
from models import UniversityAccount,SurveyResponse,SurveyResponseStaff 
from fastapi import APIRouter, Body


router = APIRouter()


# Function to update login attempts and lockout time
def update_login_attempt(username, attempts_left):
    lockout_time = None
    if attempts_left == 0:
        lockout_time = datetime.now() + timedelta(hours=2)
    collection_3.update_one({"username": username}, {"$set": {"login_attempts": attempts_left, "lockout_time": lockout_time}})

# Handle login POST request
@router.post("/login/",tags=["Login"])
async def login(username: str = Form(...), password: str = Form(...)):
    # Check if username exists in the database
    user = collection_3.find_one({"username": username})
    if user:
        # Check if the account is locked
        if user.get("lockout_time") and user["lockout_time"] > datetime.now():
            raise HTTPException(status_code=401, detail=f"Account locked until {user['lockout_time']}")
        
        # Check if the password matches
        if user["password"] == password:
            return {"message": "Login successful"}
        else:
            # Update login attempts
            attempts_left = user.get("login_attempts", 3) - 1
            update_login_attempt(username, attempts_left)
            if attempts_left > 0:
                raise HTTPException(status_code=401, detail=f"Invalid username or password. {attempts_left} attempts left.")
            else:
                raise HTTPException(status_code=401, detail=f"Account locked for 2 hours due to too many failed login attempts.")
    
    # Return 401 if credentials are invalid
    raise HTTPException(status_code=401, detail="Invalid username or password")

# Get all University enrolled
@router.get("/institutes/", response_model=list[UniversityAccount], tags=["Manage Institute"])
def get_all_institutes():
    # Retrieve all documents from the MongoDB collection
    institutes = list(collection.find({}))

    # Check if any documents were found
    if institutes:
        # Return the list of institutes
        return institutes
    else:
        raise HTTPException(status_code=404, detail="No institutes found")
    

# Endpoint to create a new university account
@router.post("/institutes/", tags=["Manage Institute"])
def create_university_account(
    university_name: str = Form(..., description="Enter the university name"),
    university_id: str = Form(..., description="Enter the university ID"),
    account_active: bool = Form(True, description="Is the account active?")
):
    try:
        # Create UniversityAccount object
        account = UniversityAccount(
            university_name=university_name,
            university_id=university_id,
            account_active=account_active
        )
        # Insert the new account into the MongoDB collection
        result = collection.insert_one(account.dict())
        # Check if the insertion was successful
        if result.inserted_id:
            return {"message": "University account created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create university account")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create university account: {str(e)}")


# Endpoint to activate a university account
@router.put("/institutes/{university_id}/activate_university_account",tags=["Manage Institute"])
def activate_account(university_id: str):
    # Update the account status in the MongoDB collection to active
    result = collection.update_one({"university_id": university_id}, {"$set": {"account_active": True}})
    # Check if the update was successful
    if result.modified_count == 1:
        return {"message": f"Account with ID {university_id} activated successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Account with ID {university_id} not found")


# Endpoint to deactivate a university account
@router.put("/institutes/{university_id}/deactivate_university_account",tags=["Manage Institute"])
def deactivate_account(university_id: str):
    # Update the account status in the MongoDB collection to inactive
    result = collection.update_one({"university_id": university_id}, {"$set": {"account_active": False}})
    # Check if the update was successful
    if result.modified_count == 1:
        return {"message": f"Account with ID {university_id} deactivated successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Account with ID {university_id} not found")

@router.put("/institutes/{university_id}/update",tags=["Manage Institute"])
async def update_account(university_id: str, account: UniversityAccount):
    existing_account = collection.find_one({"university_id": university_id})
    if existing_account:
        if existing_account["account_active"]:
            collection.update_one({"university_id": university_id}, {"$set": account.dict()})
            return {"message": "University account updated successfully"}
        else:
            raise HTTPException(status_code=403, detail="Account is not active. Cannot modify settings.")
    else:
        raise HTTPException(status_code=404, detail="University account not found")



# FASTAPI code for the Student Survey

# fastAPI endpoint to get all the surveys
@router.get("/student/survey/", response_model=list[SurveyResponse], tags=["Student survey"])
def get_all_student():
    # Retrieve all documents from the MongoDB collection
    student = list(collection_1.find({}))

    # Check if any documents were found
    if student:
        # Return the list of institutes
        return student
    else:
        raise HTTPException(status_code=404, detail="No Survey found")

# FastAPI endpoint to submit a new Student Survey
@router.post("/student/surveyresponse/", tags=["Student survey"])
def submit_student_survey(
    student_id: str = Form(...),
    university_name: str = Form(...),
    program: str = Form(...),
    feedback: str = Form(...),
    student_program_rating: int = Form(...),
    program_scores: int = Form(...),
    program_internship_rating: int = Form(...)
):
    try:
        # Create a SurveyResponse object with the form data
        response = SurveyResponse(
            student_id=student_id,
            university_name=university_name,
            program=program,
            feedback=feedback,
            student_program_rating=student_program_rating,
            program_scores=program_scores,
            program_internship_rating=program_internship_rating
        )
        
        # Insert survey response into MongoDB
        collection_1.insert_one(response.dict())
        
        return {"message": "Survey response submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to submit survey response")
    

#FastAPI endpoint to generate statistical analysis
@router.get("/student/survey/{university_name}/{program}/statistical-data", tags=["Student survey"])
def generate_statistical_analysis(university_name: str, program: str):
    try:
        # Fetch survey responses for the specified university and program
        survey_responses = list(collection_1.find({
            "university_name": university_name,
            "program": program
        }))

        if not survey_responses:
            raise HTTPException(status_code=404, detail=f"No survey responses found for university '{university_name}' and program '{program}'")

        # Initialize counters
        student_program_rating_count = 0
        program_scores_count = 0
        program_internship_rating_count = 0

        # Count occurrences of each attribute
        for response in survey_responses:
            student_program_rating_count += response.get('student_program_rating', 0)
            program_scores_count += response.get('program_scores', 0)
            program_internship_rating_count += response.get('program_internship_rating', 0)

        # Construct the analysis result
        analysis_result = {
            "university_name": university_name,
            "program": program,
            "student_program_rating_count": student_program_rating_count,
            "program_scores_count": program_scores_count,
            "program_internship_rating_count": program_internship_rating_count
        }

        return analysis_result

    except HTTPException as he:
        raise he  # Re-raise HTTPException to maintain status code and detail
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate statistical analysis")



# FASTAPI code for the Staff Survey

# fastAPI endpoint to get all the surveys
@router.get("/staff/Survey/", response_model=list[SurveyResponseStaff], tags=["Staff survey"])
def get_all_staff():
    # Retrieve all documents from the MongoDB collection
    staff = list(collection_2.find({}))

    # Check if any documents were found
    if staff:
        # Return the list of institutes
        return staff
    else:
        raise HTTPException(status_code=404, detail="No Survey found")
    
#FastAPI endpoint to submit a new Staff Survey  
@router.post("/staff/survey-response/", tags=["Staff survey"])
def submit_staff_survey(
    staff_id: str = Form(...),
    university_name: str = Form(...),
    feedback: str = Form(...),
    university_rank: int = Form(...),
    facilities: int = Form(...),
    job_satisfaction: int = Form(...),
    working_environment_rating: int = Form(...)
):
    try:
        # Create a SurveyResponseStaff object with the form data
        response = SurveyResponseStaff(
            staff_id=staff_id,
            university_name=university_name,
            feedback=feedback,
            university_rank=university_rank,
            facilities=facilities,
            job_satisfaction=job_satisfaction,
            working_environment_rating=working_environment_rating
        )
        
        # Insert staff survey response into MongoDB
        collection_2.insert_one(response.dict())
        
        return {"message": "Staff survey response submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to submit staff survey response")
    


# FastAPI endpoint to generate statistical analysis for staff survey
@router.get("/staff/survey/{university_name}/statistical-data/", tags=["Staff survey"])
def generate_statistical_analysis(university_name: str):
    try:
        # Fetch staff survey responses for the specified university from collection_2 in the database
        survey_responses = list(collection_2.find({
            "university_name": university_name
        }))

        if not survey_responses:
            raise HTTPException(status_code=404, detail=f"No survey responses found for university '{university_name}'")

        # Initialize counters
        university_rank_total = 0
        facilities_total = 0
        job_satisfaction_total = 0
        working_environment_total = 0
        num_responses = len(survey_responses)

        # Calculate total ratings
        for response in survey_responses:
            university_rank_total += response.get('university_rank', 0)
            facilities_total += response.get('facilities', 0)
            job_satisfaction_total += response.get('job_satisfaction', 0)
            working_environment_total += response.get('working_environment_rating', 0)

        # Calculate average ratings
        university_rank_avg = university_rank_total / num_responses
        facilities_avg = facilities_total / num_responses
        job_satisfaction_avg = job_satisfaction_total / num_responses
        working_environment_avg = working_environment_total / num_responses

        # Construct the analysis result
        analysis_result = {
            "university_name": university_name,
            "university_rank": university_rank_avg,
            "facilities": facilities_avg,
            "job_satisfaction": job_satisfaction_avg,
            "working_environment_rating": working_environment_avg
        }

        return analysis_result

    except HTTPException as he:
        raise he  # Re-raise HTTPException to maintain status code and detail
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate statistical analysis")