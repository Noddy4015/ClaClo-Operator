from pydantic import BaseModel

# Data model for University Account
class UniversityAccount(BaseModel):
    university_name: str
    university_id : str
    account_active: bool

# Data model for Student Survey
class SurveyResponse(BaseModel):
    student_id: str
    university_name: str
    program: str
    feedback: str
    student_program_rating: int
    program_scores: int
    program_internship_rating: int


# Data models for Staff Survey
class SurveyResponseStaff(BaseModel):
    staff_id: str
    university_name: str
    feedback: str
    university_rank: int
    facilities: int
    job_satisfaction: int
    working_environment_rating: int