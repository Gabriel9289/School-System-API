from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class MarkResponse(BaseModel):
    id: int
    subject: str
    score: float
    term: int

    class Config:
        from_attributes= True

class StudentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    grade_level: int 
    is_active: bool

    class Config:
        from_attributes= True

class StudentWithMarks(BaseModel):
    id: int
    first_name: str
    last_name: str
    grade_level: int 
    is_active: bool
    marks: List[MarkResponse] = []

    class Config:
        from_attributes= True

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    grade_level: int 

class AttendanceCodeResponse(BaseModel):
    id: int
    class_id: int
    code: str
    expires_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class AttendanceSubmit(BaseModel):
    class_id: int
    code: str

class MarkSubmit(BaseModel):
    student_id: int
    subject: str
    score: float
    term: int

class ClassPerformanceResponse(BaseModel):
    first_name: str
    last_name: str
    score: float

    class Config:
        from_attributes = True