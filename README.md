# School System API

A REST API for managing a school — built with FastAPI, SQLAlchemy, and PostgreSQL.

## Live URL

deploying on Railway: https://web-production-134b2.up.railway.app/

---

## What It Does

A fully role-based school management system where principals, teachers, parents, and students each get access to only what they need.

**Principal**
- View all students and their performance
- Create and deactivate student records
- Access a full dashboard showing totals and averages

**Teacher**
- View all students and marks
- Submit and update marks per student, subject, and term
- Generate a time-limited OTP code for attendance

**Student**
- View their own profile and marks
- Submit an OTP code to mark attendance for a class

**Parent**
- View their linked child's profile and marks

---

## Features

- JWT authentication — login returns a token, token protects every route
- Role-based access control — 403 returned automatically if the role is wrong
- OTP attendance system — teacher generates a code, students submit it within the time window, duplicates rejected
- Marks management — submit or update marks per student, subject, and term
- Performance reporting — class results ordered by score
- Principal dashboard — live counts and averages from the database

---

## Tech Stack

- **Python** — core language
- **FastAPI** — web framework and automatic API docs
- **SQLAlchemy** — ORM for database access
- **PostgreSQL** — database
- **JWT (python-jose)** — authentication tokens
- **bcrypt (passlib)** — password hashing
- **Railway** — deployment and hosted database

---

## Running Locally

**1. Clone the repository**

```
git clone https://github.com/Gabriel9289/school-system-api.git
cd school-system-api
```

**2. Create a virtual environment and install dependencies**

```
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

**3. Create a `.env` file in the project root**

```
DB_HOST=localhost
DB_NAME=school_system
DB_USER=postgres
DB_PASSWORD=your_password_here
SECRET_KEY=your_secret_key_here
```

**4. Create the database tables**

```
python create_tables.py
```

**5. Start the server**

```
uvicorn main:app --reload
```

**6. Open the docs**

```
http://localhost:8000/docs
```

---

## API Overview

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | /register | Public | Register a new user |
| POST | /login | Public | Login and receive a JWT token |
| GET | /students | Teacher, Principal | List all students |
| GET | /student/id/{id} | Teacher, Principal | Get one student with marks |
| POST | /student/create | Principal | Create a new student |
| PUT | /student/update/{id} | Teacher, Principal | Update student details |
| DELETE | /student/delete/{id} | Principal | Deactivate a student |
| POST | /marks/submit | Teacher, Principal | Submit or update a mark |
| GET | /performance/{subject}/{term} | Teacher, Principal | Class performance report |
| POST | /classes/{id}/attendance-code | Teacher, Principal | Generate OTP attendance code |
| POST | /attendance/submit | Student | Submit attendance code |
| GET | /my-profile | Student | View own profile and marks |
| GET | /my-marks | Student | View own marks |
| GET | /my-child | Parent | View linked child's profile |
| GET | /principal/dashboard | Principal | Full school summary |

---

## Project Structure

```
school_api/
├── main.py          — routes and endpoints
├── database.py      — SQLAlchemy models and database connection
├── schemas.py       — Pydantic request and response models
├── services.py      — database query logic
├── auth.py          — JWT tokens, password hashing, role checking
├── create_tables.py — run once to create all database tables
├── requirements.txt — Python dependencies
└── Procfile         — Railway startup command
```

---

## Author

Gabriel — [github.com/Gabriel9289](https://github.com/Gabriel9289)

Backend developer focused on Python, FastAPI, PostgreSQL, and systems that actually work.
