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

class JobPostingResponse(JobPostingCreate):
    id: int

    class Config:
       from_attributes = True




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
