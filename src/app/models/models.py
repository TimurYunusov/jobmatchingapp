from enum import Enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum as SqlEnum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class LocationType(str, Enum):
    remote = "REMOTE"
    hybrid = "HYBRID"
    onsite = "ON_SITE"

class EmploymentType(str, Enum):
    full_time = "FULLTIME"
    part_time = "PARTTIME"
    contract = "CONTRACT"

class JobPosting(Base):
    __tablename__ = "jobPosting"  

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("Company.id"))
    title = Column(String, nullable=False)
    compensation_min = Column(Float, nullable=True)
    compensation_max = Column(Float, nullable=True)
    location_type = Column(
        SqlEnum(LocationType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False
    )
    employment_type = Column(
        SqlEnum(EmploymentType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False
    )
    description = Column(String, nullable=True)
    company = relationship("Company", back_populates="job_postings")

class Company(Base):
    __tablename__ = "Company"  # matches your Supabase table exactly

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    url = Column(String, nullable=True)
    headcount = Column(Integer, nullable=True)
    country = Column(String, nullable=True)
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)
    glassdoor = Column(String, nullable=True)
    isPublic = Column(Boolean, default=False)

    job_postings = relationship("JobPosting", back_populates="company")
