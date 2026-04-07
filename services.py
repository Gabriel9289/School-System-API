from sqlalchemy.orm import Session
from database import Student,Mark,User,AttendanceCode, Attendance, Enrollment
from schemas import StudentCreate
from typing import Optional
from auth import hash_password
from datetime import datetime, timedelta
import random
import string


def create_user(db,email:str,password:str,role:str):
    hashed = hash_password(password)
    user = User(email=email,hashed_password=hashed,role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



def get_user_by_email(db,email:str):
    return db.query(User).filter(User.email == email).first()



#GET all students

def get_all_students( db:Session, grade: Optional[int], active: Optional[bool]):
    query= db.query(Student)
    if grade is not None:
        query= query.filter(Student.grade_level== grade)
    if active is not None:
        query= query.filter(Student.is_active==active)
    return query.all()


def get_all_student_marks(db:Session, subject: Optional[str], term: Optional[int]):
    query= db.query(Mark)
    if subject is not None:
        query= query.filter(Mark.subject == subject)
    if term is not None:
        query= query.filter(Mark.term == term)
    return query.all()


def get_student_by_id(db:Session,student_id:int):
    return db.get(Student,student_id)


#POST Create a student
def create_student(data: StudentCreate,db: Session):
    new_student= Student(first_name=data.first_name,
                         last_name=data.last_name,
                         grade_level=data.grade_level)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


def change_details(db: Session, data,student):
    student.first_name = data.first_name
    student.last_name = data.last_name
    student.grade_level = data.grade_level
    db.commit()
    db.refresh(student)
    return student




def deactivate_student(db: Session,student):
    student.is_active =False
    db.commit()
    db.refresh(student)
    return student

 #here
def generate_attendance_code(db: Session, class_id: int) -> AttendanceCode:
    # Deactivate any existing active codes for this class
    existing = db.query(AttendanceCode).filter(
        AttendanceCode.class_id == class_id,
        AttendanceCode.is_active == True
    ).all()
    for code in existing:
        code.is_active = False
    db.commit()

    # Generate a new 6-character code
    new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    expires = datetime.now() + timedelta(hours=1)

    attendance_code = AttendanceCode(
        class_id=class_id,
        code=new_code,
        expires_at=expires,
        is_active=True
    )
    db.add(attendance_code)
    db.commit()
    db.refresh(attendance_code)
    return attendance_code

def submit_attendance(db: Session, student_id: int, class_id: int, code: str):
    # Find the active code for this class
    active_code = db.query(AttendanceCode).filter(
        AttendanceCode.class_id == class_id,
        AttendanceCode.is_active == True,
        AttendanceCode.code == code
    ).first()

    if not active_code:
        return None, "Invalid or inactive code"

    # Check if expired
    if datetime.now() > active_code.expires_at:
        active_code.is_active = False
        db.commit()
        return None, "Code has expired"

    # Check if student is enrolled in this class
    enrolled = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.class_id == class_id
    ).first()

    if not enrolled:
        return None, "Student not enrolled in this class"

    # Check if already marked attendance today
    today_start = datetime.now().replace(hour=0, minute=0, second=0)
    already_marked = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.class_id == class_id,
        Attendance.marked_at >= today_start
    ).first()

    if already_marked:
        return None, "Attendance already marked for today"

    # Record attendance
    record = Attendance(
        student_id=student_id,
        class_id=class_id,
        code_used=code
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record, "Attendance marked successfully"

#AND


def submit_mark(db: Session, student_id: int, subject: str, score: float, term: int):
    # Check if mark already exists for this student/subject/term
    existing = db.query(Mark).filter(
        Mark.student_id == student_id,
        Mark.subject == subject,
        Mark.term == term
    ).first()

    if existing:
        # Update existing mark
        existing.score = score
        db.commit()
        db.refresh(existing)
        return existing

    # Create new mark
    mark = Mark(
        student_id=student_id,
        subject=subject,
        score=score,
        term=term
    )
    db.add(mark)
    db.commit()
    db.refresh(mark)
    return mark

def get_student_marks(db: Session, student_id: int):
    return db.query(Mark).filter(Mark.student_id == student_id).all()

def get_class_performance(db: Session, subject: str, term: int):
    from sqlalchemy import func
    return db.query(
        Student.first_name,
        Student.last_name,
        Mark.score
    ).join(Mark, Student.id == Mark.student_id).filter(
        Mark.subject == subject,
        Mark.term == term
    ).order_by(Mark.score.desc()).all()

