from pydantic import BaseModel

# Data models
class UniversityAccount(BaseModel):
    university_name: str
    university_id : str
    account_active: bool

#FastAPI code for Student surveys
class SurveyResponse(BaseModel):
    student_id: str
    university_name: str
    program: str
    feedback: str
    student_program_rating: int
    program_scores: int
    program_internship_rating: int


#FastAPI code for Staff surveys
class SurveyResponseStaff(BaseModel):
    staff_id: str
    university_name: str
    feedback: str
    university_rank: int
    facilities: int
    job_satisfaction: int
    working_environment_rating: int