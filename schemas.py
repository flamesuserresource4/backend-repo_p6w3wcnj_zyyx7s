"""
Database Schemas for Flames.blue

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase of the class name.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime

# Core users
class Candidate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password_hash: Optional[str] = None

    # Onboarding fields
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    relocate_countries: List[str] = Field(default_factory=list)
    job_types: List[Literal["Permanent","Part-time","Per diem","Live-in"]] = Field(default_factory=list)
    search_status: Optional[Literal["Just started","Interviewing","Not actively looking"]] = None
    start_date_option: Optional[Literal["Immediately","Few weeks","Few months","Specific date"]] = None
    start_date_specific: Optional[date] = None
    experience_years: Optional[float] = None

    graduate: Optional[bool] = None
    graduation_date: Optional[date] = None
    school: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    gpa: Optional[str] = None

    specialties: List[str] = Field(default_factory=list)
    resume_url: Optional[str] = None

    # Eligibility & Compliance (Saudi-specific)
    visa_status: Optional[str] = None
    residency: Optional[str] = None
    licensing: Optional[str] = None
    biometric_certificate: Optional[bool] = None

    # System
    role: Literal["candidate"] = "candidate"
    fit_score: Optional[int] = Field(default=None, ge=0, le=100)
    compliance_flags: List[str] = Field(default_factory=list)

class Recruiter(BaseModel):
    company_name: str
    email: EmailStr
    phone: Optional[str] = None
    password_hash: Optional[str] = None
    role: Literal["recruiter"] = "recruiter"

class Admin(BaseModel):
    email: EmailStr
    password_hash: str
    role: Literal["admin"] = "admin"

# Jobs & Applications
class Job(BaseModel):
    title: str
    location_country: str
    location_city: Optional[str] = None
    employment_type: Literal["Permanent","Part-time","Per diem","Live-in"]
    description: Optional[str] = None
    specialties: List[str] = Field(default_factory=list)
    recruiter_id: Optional[str] = None
    status: Literal["open","closed"] = "open"

class Application(BaseModel):
    candidate_id: str
    job_id: str
    status: Literal["applied","shortlisted","offered","hired","rejected"] = "applied"
    fit_score: Optional[int] = Field(default=None, ge=0, le=100)

class Swipe(BaseModel):
    candidate_id: str
    job_id: str
    direction: Literal["right","left"]

# Contracts & Payments
class Contract(BaseModel):
    job_id: str
    candidate_id: str
    recruiter_id: str
    terms: Optional[str] = None
    candidate_signed_at: Optional[datetime] = None
    recruiter_signed_at: Optional[datetime] = None
    status: Literal["draft","candidate_signed","fully_signed"] = "draft"

class Payment(BaseModel):
    recruiter_id: str
    contract_id: str
    amount: float
    currency: str = "USD"
    status: Literal["pending","paid","failed","refunded"] = "pending"

# Messaging
class Message(BaseModel):
    sender_id: str
    receiver_id: str
    body: str
    read: bool = False

