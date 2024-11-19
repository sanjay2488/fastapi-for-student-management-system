from fastapi import Depends, FastAPI, HTTPException  # Import FastAPI and related modules.
from pydantic import BaseModel, EmailStr  # Import Pydantic BaseModel and Email validation type.
from typing import List  # Import List for type hinting.
from sqlalchemy import create_engine, Column, Integer, String  # SQLAlchemy utilities for ORM mapping.
from sqlalchemy.ext.declarative import declarative_base  # Base class for SQLAlchemy models.
from sqlalchemy.orm import sessionmaker, Session  # Session and sessionmaker for database operations.

# SQLAlchemy configuration
DATABASE_URL = "mysql://root:Prema$1998@localhost/student_management_1"  # Database connection string.

# Create SQLAlchemy engine and sessionmaker
engine = create_engine(DATABASE_URL, connect_args={"charset": "utf8mb4"})  # Create the SQLAlchemy engine with charset.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Session factory for managing DB sessions.

# Base class for models
Base = declarative_base()  # Base class for defining SQLAlchemy models.

# Data Model for a Student (SQLAlchemy)
class Student(Base):
    """
    SQLAlchemy model representing the 'students' table in the database.
    """
    __tablename__ = "students"  # Table name in the database.
    id = Column(Integer, primary_key=True, index=True)  # Primary key column with an index.
    name = Column(String(255), nullable=False)  # Name column, cannot be null.
    age = Column(Integer, nullable=False)  # Age column, cannot be null.
    address = Column(String(500), nullable=False)  # Address column, cannot be null.
    email = Column(String(255), unique=True, nullable=False)  # Email column, must be unique and cannot be null.

# FastAPI instance
app = FastAPI()  # Create an instance of the FastAPI application.

# Dependency to get the DB session
def get_db():
    """
    Dependency that provides a database session for each request.
    Ensures proper session handling with context management.
    """
    db = SessionLocal()  # Create a new session.
    try:
        yield db  # Yield the session to the endpoint function.
    finally:
        db.close()  # Ensure the session is closed after the request.

# Data model for a Student (Pydantic) for validation
class StudentCreate(BaseModel):
    """
    Pydantic schema for validating input data when creating or updating students.
    """
    name: str  # Name field.
    age: int  # Age field.
    address: str  # Address field.
    email: EmailStr  # Email field, validated as a proper email address.

class StudentOut(StudentCreate):
    """
    Pydantic schema for output data when returning student information.
    Includes the student ID.
    """
    id: int  # Student ID field.

    class Config:
        orm_mode = True  # Enable automatic conversion of ORM objects to dict.

# Initialize the database (create tables if they don't exist)
Base.metadata.create_all(bind=engine)  # Automatically create the 'students' table in the database.

# Routes

@app.get("/students", response_model=List[StudentOut])
def get_students(db: Session = Depends(get_db)):
    """
    Endpoint to retrieve all students.
    - Queries the database for all students and returns them as a list.
    """
    students = db.query(Student).all()  # Fetch all students from the database.
    return students  # Return the list of students.

@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a specific student by ID.
    - Queries the database for the student with the given ID.
    - Raises a 404 error if the student is not found.
    """
    student = db.query(Student).filter(Student.id == student_id).first()  # Query the student by ID.
    if not student:  # If no student is found, raise a 404 error.
        raise HTTPException(status_code=404, detail="Student not found")
    return student  # Return the student data.

@app.post("/students", response_model=StudentOut)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new student.
    - Accepts student data as input.
    - Adds the student to the database and returns the created student.
    """
    db_student = Student(
        name=student.name,  # Set the student's name.
        age=student.age,  # Set the student's age.
        address=student.address,  # Set the student's address.
        email=student.email,  # Set the student's email.
    )
    db.add(db_student)  # Add the new student to the session.
    db.commit()  # Commit the session to save the student to the database.
    db.refresh(db_student)  # Refresh the instance to get the updated data.
    return db_student  # Return the created student.

@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, updated_student: StudentCreate, db: Session = Depends(get_db)):
    """
    Endpoint to update an existing student.
    - Queries the database for the student by ID.
    - Updates the student's details if they exist.
    - Raises a 404 error if the student is not found.
    """
    db_student = db.query(Student).filter(Student.id == student_id).first()  # Query the student by ID.
    if not db_student:  # If no student is found, raise a 404 error.
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_student.name = updated_student.name  # Update the student's name.
    db_student.age = updated_student.age  # Update the student's age.
    db_student.address = updated_student.address  # Update the student's address.
    db_student.email = updated_student.email  # Update the student's email.
    
    db.commit()  # Commit the session to save the changes.
    db.refresh(db_student)  # Refresh the instance to get the updated data.
    return db_student  # Return the updated student.

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to delete a student by ID.
    - Queries the database for the student by ID.
    - Deletes the student if they exist.
    - Raises a 404 error if the student is not found.
    """
    db_student = db.query(Student).filter(Student.id == student_id).first()  # Query the student by ID.
    if not db_student:  # If no student is found, raise a 404 error.
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)  # Delete the student from the session.
    db.commit()  # Commit the session to apply the deletion.
    return {"message": f"Student with ID {student_id} deleted"}  # Return a success message.

