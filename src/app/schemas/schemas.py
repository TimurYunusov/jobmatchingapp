from typing import List
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum

class LocationType(str, Enum):
    remote = "REMOTE"
    hybrid = "HYBRID"
    onsite = "ON_SITE"

class EmploymentType(str, Enum):
    full_time = "FULLTIME"
    part_time = "PARTTIME"
    contract = "CONTRACT"

class JobPostingCreate(BaseModel):
    company_id: int
    title: str
    compensation_min: float | None = None
    compensation_max: float | None = None
    location_type: LocationType
    employment_type: EmploymentType
    description: str | None = None

class JobPostingResponse(JobPostingCreate):
    id: int
    description: str | None = None

    class Config:
       from_attributes = True

class GenerateDescriptionRequest(BaseModel):
    required_tools: List[str]

class GenerateDescriptionResponse(BaseModel):
    job_id: int
    description: str
    generated_at: datetime


class CompanyCreate(BaseModel):
    name: str
    industry: str | None = None
    url: str | None = None
    headcount: int | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    glassdoor: str | None = None
    isPublic: bool = False

class CompanyResponse(CompanyCreate):
    id: int

    class Config:
        from_attributes = True

class CompanyCreates(CompanyCreate):
    pass

class CompanyUpdates(CompanyCreate):
    name: Optional[str] = None
    

class CompanyDeletes(BaseModel):
    pass

class JobDescriptionSection(BaseModel):
    title: str
    content: str

class StructuredJobDescription(BaseModel):
    title: str
    overview: str
    responsibilities: List[str]
    requirements: List[str]
    qualifications: List[str]
    benefits: List[str]
    company_culture: Optional[str] = None
    location_info: Optional[str] = None
    compensation_info: Optional[str] = None
