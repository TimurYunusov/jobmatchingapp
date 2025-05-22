from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.app.db import get_db
from src.app.models import models
from src.app.schemas import schemas

router = APIRouter()

@router.get("/job_postings")
def get_all_job_postings(db: Session = Depends(get_db)):
    result = db.execute(text('SELECT * FROM "jobPosting"'))
    
    rows = result.fetchall()

    #format each row as a String
    output = []
    for row in rows:
        output.append(str(dict(row._mapping)))

    return output    
# ---------- CREATE JOB POSTING ----------
@router.post("/job-postings", response_model=schemas.JobPostingResponse)
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
@router.get("/job-postings/{job_id}", response_model=schemas.JobPostingResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job

# ---------- UPDATE ----------
@router.put("/job-postings/{job_id}", response_model=schemas.JobPostingResponse)
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
@router.delete("/job-postings/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    db.delete(job)
    db.commit()
    return {"status": "success", "detail": f"Job posting {job_id} deleted"}