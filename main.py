from enum import Enum
from http.client import HTTPException
from typing import Optional
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import Float, create_engine, Column, Integer, String, select, text, Enum as SqlEnum
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import models, schemas

#DATABASE_URL = "postgresql://postgres:a9Xk0ZyLegnQ4n4K@db.rphwhyxwaacqlrlljzqu.supabase.co:5432/postgres"
DATABASE_URL = "postgresql://postgres.rphwhyxwaacqlrlljzqu:a9Xk0ZyLegnQ4n4K@aws-0-us-east-2.pooler.supabase.com:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
app = FastAPI()
Base = declarative_base()

class ApplicationUpdate(BaseModel):
    email: Optional[str] = None
    job_id: Optional[str] = None
       
applications = []

class Application(BaseModel):
    candidate_id: str
    name: str
    email: str
    job_id: Optional[str] = None
    company_name: str

# Enums for location and employment types
class LocationType(str, Enum):
    remote = "REMOTE"
    hybrid = "HYBRID"
    onsite = "ON_SITE"

class EmploymentType(str, Enum):
    full_time = "FULLTIME"
    part_time = "PARTTIME"
    contract = "CONTRACT"
  

# JobPosting Pydantic model
class JobPosting(Base):
    __tablename__ = "jobPosting"  # Make sure it matches your Supabase table name

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer)
    title = Column(String)
    compensation_min = Column(Float)
    compensation_max = Column(Float)
    location_type = Column(SqlEnum(LocationType), nullable=False)
    employment_type = Column(SqlEnum(EmploymentType), nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/jobs")
def get_all_job_postings(db: Session = Depends(get_db)):
    result = db.execute(text('SELECT * FROM "jobPosting"'))
    
    rows = result.fetchall()

    #format each row as a String
    output = []
    for row in rows:
        output.append(str(dict(row._mapping)))

    return output    
# ---------- CREATE JOB POSTING ----------
@app.post("/job-postings", response_model=schemas.JobPostingResponse)
def create_job(job_posting: schemas.JobPostingCreate, db: Session = Depends(get_db)):

    job_model = models.JobPosting(company_id=job_posting.company_id,
        title=job_posting.title,
        compensation_min=job_posting.compensation_min,
        compensation_max=job_posting.compensation_max,
        location_type=job_posting.location_type.value,
        employment_type=job_posting.employment_type.value)
    db.add(job_model)
    db.commit()
    db.refresh(job_model)
    return job_model

# ---------- READ ONE ----------
@app.get("/job-postings/{job_id}", response_model=schemas.JobPostingResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job

# ---------- UPDATE ----------
@app.put("/job-postings/{job_id}", response_model=schemas.JobPostingResponse)
def update_job(job_id: int, job_update: schemas.JobPostingCreate, db: Session = Depends(get_db)):
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    job.company_id = job_update.company_id
    job.title = job_update.title
    job.compensation_min = job_update.compensation_min
    job.compensation_max = job_update.compensation_max
    job.location_type = job_update.location_type.value
    job.employment_type = job_update.employment_type.value

    db.commit()
    db.refresh(job)
    return job

# ---------- DELETE ----------
@app.delete("/job-postings/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    db.delete(job)
    db.commit()
    return {"status": "success", "detail": f"Job posting {job_id} deleted"}

#Company Endpoints:
@app.post("/add_company", response_model=schemas.CompanyResponse)
def add_company(
    company: schemas.CompanyCreate,
    db: Session = Depends(get_db)
):
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

# Endpoint to GET all companies
@app.get("/get_companies", response_model=list[schemas.CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    companies = db.query(models.Company).all()
    return companies

# ---------------- READ (GET ONE) ----------------
@app.get("/companies/{company_id}", response_model=schemas.CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

# ---------------- UPDATE ----------------
@app.put("/companies/{company_id}", response_model=schemas.CompanyResponse)
def update_company(
    company_id: int, 
    company_update: schemas.CompanyCreate,
    db: Session = Depends(get_db)
):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for key, value in company_update.dict().items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)
    return company

# ---------------- DELETE ----------------
@app.delete("/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db.delete(company)
    db.commit()
    return {"status": "success", "detail": f"Company {company_id} deleted"}







@app.post("/applications")
def post_application(application: Application):
    applications.append(application)
    return {
  "status": "success",
  "message": f"Application submitted for {application.name}"
}

@app.get("/applications/")
def get_applications(company_name: str = None, candidate_email: str = None):
    filtered_applications = applications
    if company_name:
        print(f"for {company_name} there are {len(filtered_applications)} applications")
        filtered_applications = [application for application in filtered_applications if application.company_name == company_name]
    if candidate_email:
        print(f"for {candidate_email} there are {len(filtered_applications)} applications")
        filtered_applications = [application for application in filtered_applications if application.email == candidate_email]
        
    return {
        "status": "success",
        "message": "Applications fetched successfully",
        "applications": filtered_applications
    }
@app.get("/applications/{candidate_id}")
def get_application(candidate_id: str):
    for application in applications:
        if application.candidate_id == candidate_id:
            return {
                f"Application found for candidate ID: {candidate_id}",
                f"Application: {application}"
            }
    return {
        "status": "error",
        "message": f"Application not found for candidate ID: {candidate_id}"
    }

#accepts a json object with the following fields:
#email
#job_id
@app.put("/applications/{candidate_id}")
def update_application(candidate_id: str, application: Application):
    for app in applications:  # Use 'app' as the variable name for clarity
        if app.candidate_id == candidate_id:
            # Update the existing application with the new data
            app.email = application.email
            app.job_id = application.job_id
            app.company_name = application.company_name
            app.name = application.name  # If you want to update the name as well
            return {
                f"Application for {candidate_id} successfully updated"
            }
    return {
        "status": "error",
        "message": f"Application not found for candidate ID: {candidate_id}"
    }


@app.patch("/applications/{candidate_id}")
def patch_application(candidate_id: str, application: ApplicationUpdate):
    for app in applications:
        if app.candidate_id == candidate_id:
            updated_fields = []
            if application.email is not None:
                app.email = application.email
                updated_fields.append("email")
            if application.job_id is not None:
                app.job_id = application.job_id
                updated_fields.append("job_id")
            
            if updated_fields:
                return {
                    "status": "success",
                    "message": f"Application for {candidate_id} successfully updated. Updated fields: {', '.join(updated_fields)}"
                }
            else:
                return {
                    "status": "info",
                    "message": "No fields were updated."
                }
    
    return {
        "status": "error",
        "message": f"Application not found for candidate ID: {candidate_id}"
    }

@app.delete("/applications/{candidate_id}")
def delete_application(candidate_id: str):
    for app in applications:
        if app.candidate_id == candidate_id:
            applications.remove(app)
            return {
                "status": "success",
                "message": f"Application for {candidate_id} successfully deleted"
            }
    return {
        "status": "error",
        "message": f"Application not found for candidate ID: {candidate_id}"
    }

