from fastapi import FastAPI ,Depends,HTTPException
from sqlalchemy.orm import Session
from database import get_db,Student,Mark
from schemas import StudentResponse,StudentWithMarks,StudentCreate,MarkResponse,UserCreate,TokenResponse
from typing import Optional,List
from services import get_all_students,get_student_by_id,create_student,get_all_student_marks,deactivate_student,change_details,get_user_by_email,create_user
from auth import verify_password,create_access_token,get_current_user,require_roles

from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
app = FastAPI()

#start

from services import (
    generate_attendance_code,
    submit_attendance,
    submit_mark,
    get_student_marks,
    get_class_performance
)
from schemas import (
    AttendanceCodeResponse,
    AttendanceSubmit,
    MarkSubmit,
    ClassPerformanceResponse
)

# TEACHER — Generate attendance code for a class
@app.post("/classes/{class_id}/attendance-code",
          response_model=AttendanceCodeResponse)
def create_attendance_code(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["teacher", "principal"]))
):
    return generate_attendance_code(db, class_id)

# STUDENT — Submit attendance using a code
@app.post("/attendance/submit")
def mark_attendance(
    data: AttendanceSubmit,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["student"]))
):
    user = get_user_by_email(db, current_user["sub"])
    if not user.student_id:
        raise HTTPException(status_code=400, detail="No student linked to account")
    record, message = submit_attendance(
        db, user.student_id, data.class_id, data.code
    )
    if not record:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "marked_at": record.marked_at}

# TEACHER — Submit or update a mark
@app.post("/marks/submit", response_model=MarkResponse)
def add_mark(
    data: MarkSubmit,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["teacher", "principal"]))
):
    return submit_mark(db, data.student_id, data.subject, data.score, data.term)

# TEACHER/PRINCIPAL — View class performance
@app.get("/performance/{subject}/{term}",
         response_model=List[ClassPerformanceResponse])
def class_performance(
    subject: str,
    term: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["teacher", "principal"]))
):
    return get_class_performance(db, subject, term)

# STUDENT — View own marks
@app.get("/my-marks", response_model=List[MarkResponse])
def my_marks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["student"]))
):
    user = get_user_by_email(db, current_user["sub"])
    if not user.student_id:
        raise HTTPException(status_code=400, detail="No student linked to account")
    return get_student_marks(db, user.student_id)

# STUDENT — Own profile
@app.get("/my-profile", response_model=StudentWithMarks)
def my_profile_student(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["student"]))
):
    user = get_user_by_email(db, current_user["sub"])
    if not user.student_id:
        raise HTTPException(status_code=400, detail="No student linked to account")
    student = get_student_by_id(db, user.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# PRINCIPAL — Full dashboard summary
@app.get("/principal/dashboard")
def principal_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["principal"]))
):
    from sqlalchemy import func
    total_students = db.query(func.count(Student.id)).scalar()
    active_students = db.query(func.count(Student.id)).filter(
        Student.is_active == True
    ).scalar()
    total_marks = db.query(func.count(Mark.id)).scalar()
    avg_score = db.query(func.avg(Mark.score)).scalar()

    return {
        "total_students": total_students,
        "active_students": active_students,
        "total_marks": total_marks,
        "overall_average": round(float(avg_score), 2) if avg_score else 0
    }
#END


@app.get("/health")
def health(db:Session = Depends(get_db)):
    return {"databse":"connected","vserion":"1.0","status":"ok"} 



@app.get("/me")
def who_am_i(current_user: dict = Depends(get_current_user),current_role: dict = Depends(require_roles(["parent","teacher","principal"]))):
    return {"email":current_user["sub"],"role":current_user["role"]}

@app.get("/dashboard")
def dashboard(current_user: dict = Depends(get_current_user),current_role: dict = Depends(require_roles(["teacher","principal"]))):
    role = current_user["role"]
    if role == "principal":
        return {"message":"Welcome principal. You can see everything."}
    elif role == "teacher":
        return {"message":"Welcome Teacher. You can see your classes."}
    if role == "parent":
        return {"message":"Welcome parent. You can see your child's data."}
    else:
        return {"message":"Welcome Guest. You have limited access."}

#access auth
@app.post("/register",status_code=201)
def register(data: UserCreate,db:Session=Depends(get_db)):
    existing = get_user_by_email(db,data.email)
    if existing:
        raise HTTPException(status_code=404,detail="Email already registered")
    user = create_user(db,data.email,data.password,data.role)
    return {"message":  f"User {user.email} created"}



@app.post("/login", response_model=TokenResponse)
def login(data: UserCreate,db:Session = Depends(get_db)):
    user = get_user_by_email(db,data.email)
    if not user or not verify_password(data.password,user.hashed_password):
        raise HTTPException(status_code=401,detail="Invalid credentials")
    token = create_access_token({"sub": user.email,"role":user.role})
    return {"access_token":token,"token_type":"bearer"}



@app.get("/students/me")
def my_profile(current_user: dict = Depends(get_current_user),current_role: dict = Depends(require_roles(["parent","teacher","principal"]))):
    return {"logged_in_as": current_user["sub"],"role":current_user["role"]}

 

#GET all students
@app.get("/students",response_model=List[StudentResponse])
def list_students( grade: Optional[int]= None,
                  active: Optional[bool]= None,
                  db:Session= Depends(get_db),
                  current_role: dict = Depends(require_roles(["teacher","principal"]))):
    
    return get_all_students(db,grade,active)



#GET all student marks
@app.get("/students/marks",response_model=List[MarkResponse])
def list_mark( subject: Optional[str]= None, term: Optional[int]= None, db:Session= Depends(get_db),current_role: dict = Depends(require_roles(["teacher","principal"]))):
    
    return get_all_student_marks(db,subject,term)



#GET one student by ID
@app.get("/student/id/{student_id}", response_model=StudentWithMarks)
def student_detail(student_id:int,db:Session= Depends(get_db),current_role: dict = Depends(require_roles(["teacher","principal"]))):
    student = get_student_by_id(db,student_id)
    if not student:
        raise HTTPException(status_code=404,detail="student ID not found")
    return student





#POST Create a student
@app.post("/student/create",response_model=StudentResponse,status_code=201)
def create_student(data: StudentCreate,db: Session = Depends(get_db),current_role: dict = Depends(require_roles(["principal"]))):
    new_student= Student(first_name=data.first_name,
                         last_name=data.last_name,
                         grade_level=data.grade_level)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student



#PUT update a student's grade 
@app.put("/student/update/{student_id}",response_model=StudentResponse)
def update_student(student_id: int,data: StudentCreate,db:Session = Depends(get_db),current_role: dict = Depends(require_roles(["teacher","principal"]))):
    student = db.get(Student,student_id)
    if not student:
        raise HTTPException(status_code=404,detail="Student not found")
    changed = change_details(db, data,student)
    """student.first_name = data.first_name
    student.last_name = data.last_name
    student.grade_level = data.grade_level
    db.commit()
    db.refresh(student)"""
    return changed



#DELETE a student
@app.delete("/student/delete/{student_id}",status_code=204)
def delete_student(student_id: int,db:Session = Depends(get_db),current_role: dict = Depends(require_roles(["principal"]))):
    student = db.get(Student,student_id)
    if not student:
        raise HTTPException(status_code=404,detail="Student not found")
    del_student = deactivate_student(db ,student)
    #student.is_active =False - db.commit()- db.refresh(student)
    return del_student

@app.get("/my-child",response_model=StudentWithMarks)
def get_my_child(db: Session = Depends(get_db),
                 current_role: dict = Depends(require_roles(["parent"]))):
    user = get_user_by_email(db,current_role["sub"])
    if not user.student_id:
        raise HTTPException(status_code=404, detail="No child licked to this account")
    student = get_student_by_id(db,user.student_id)
    if not student:
        raise HTTPException(status_code=404,detail="Student not found")
    return student
