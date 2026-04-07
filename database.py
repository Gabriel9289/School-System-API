from sqlalchemy import create_engine,Column,Integer,String,Boolean,Numeric,DateTime,ForeignKey,Enum
from sqlalchemy.orm import DeclarativeBase ,Session,relationship
from dotenv import load_dotenv
from datetime import datetime
import os
import enum


load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}"

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

class RoleEnum(str,enum.Enum):
    student = "student"
    teacher = "teacher"
    parent = "parent"
    principal = "principal"

class User(Base):
    __tablename__ ="users"
    id = Column(Integer,primary_key=True)
    email = Column(String(255),unique=True,nullable=False)
    hashed_password = Column(String(255),nullable=False)
    role = Column(Enum(RoleEnum),nullable=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime,default=datetime.now)
    student_id = Column(Integer,ForeignKey("students.id"),nullable=True)


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer,primary_key=True)
    first_name = Column(String(100),nullable=False)
    last_name = Column(String(100),nullable=False)
    grade_level = Column(Integer,nullable=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime,default=datetime.now)
    marks = relationship("Mark",back_populates="student")


class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer,primary_key=True)
    student_id = Column(Integer,ForeignKey("students.id"),nullable=False)
    subject = Column(String(100),nullable=False)
    score = Column(Numeric(5,2),nullable=False)
    term = Column(Integer,nullable=False)
    student = relationship("Student",back_populates="marks")


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    classes = relationship("Class", back_populates="teacher")

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    grade_level = Column(Integer, nullable=False)
    subject = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    teacher = relationship("Teacher", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="class_")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.now)
    student = relationship("Student", backref="enrollments")
    class_ = relationship("Class", back_populates="enrollments")

class AttendanceCode(Base):
    __tablename__ = "attendance_codes"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    code = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    code_used = Column(String(10), nullable=False)
    marked_at = Column(DateTime, default=datetime.now)
    student = relationship("Student", backref="attendance")


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()