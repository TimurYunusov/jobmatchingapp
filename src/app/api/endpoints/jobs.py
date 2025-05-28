from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.app.logging_config import logger

from src.app.db import get_db
from src.app.models import models
from src.app.schemas import schemas
from openai import OpenAI


router = APIRouter()

@router.get("/get_job_postings")
def get_all_job_postings(db: Session = Depends(get_db)):
    logger.info("Fetching all job postings")
    result = db.execute(text('SELECT * FROM "job_posting"'))
    
    rows = result.fetchall()

    #format each row as a String
    output = []
    for row in rows:
        output.append(str(dict(row._mapping)))

    logger.info(f"Retrieved {len(output)} job postings")
    return output    
# ---------- CREATE JOB POSTING ----------
@router.post("/job-postings", response_model=schemas.JobPostingResponse)
def create_job(job_posting: schemas.JobPostingCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating job posting: {job_posting.title}")
    job_model = models.JobPosting(company_id=job_posting.company_id,
        title=job_posting.title,
        compensation_min=job_posting.compensation_min,
        compensation_max=job_posting.compensation_max,
        location_type=job_posting.location_type.value,
        employment_type=job_posting.employment_type.value)
    db.add(job_model)
    db.commit()
    db.refresh(job_model)
    logger.info(f"Job posting created with ID: {job_model.id} and title: {job_model.title}")
    return job_model

# ---------- READ ONE ----------
@router.get("/job-postings/{job_id}", response_model=schemas.JobPostingResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching job posting with ID: {job_id}")
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        logger.error(f"Job posting with ID {job_id} not found")
        raise HTTPException(status_code=404, detail="Job posting not found")
    logger.info(f"Job posting retrieved: {job.title}")
    return job

# ---------- UPDATE ----------
@router.put("/job-postings/{job_id}", response_model=schemas.JobPostingResponse)
def update_job(job_id: int, job_update: schemas.JobPostingCreate, db: Session = Depends(get_db)):
    logger.info(f"Updating job posting with ID: {job_id}")
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        logger.error(f"Job posting with ID {job_id} not found")
        raise HTTPException(status_code=404, detail="Job posting not found")

    job.company_id = job_update.company_id
    job.title = job_update.title
    job.compensation_min = job_update.compensation_min
    job.compensation_max = job_update.compensation_max
    job.location_type = job_update.location_type.value
    job.employment_type = job_update.employment_type.value

    db.commit()
    db.refresh(job)
    logger.info(f"Job posting updated: {job.title}")
    return job

# ---------- DELETE ----------
@router.delete("/job-postings/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting job posting with ID: {job_id}")
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        logger.error(f"Job posting with ID {job_id} not found")
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    db.delete(job)
    db.commit()
    logger.info(f"Job posting with ID {job_id} deleted")
    return {"status": "success", "detail": f"Job posting {job_id} deleted"}

# ---------- GENERATE DESCRIPTION ----------
@router.post("/{id}/description", response_model=schemas.GenerateDescriptionResponse)
async def generate_job_description(
    id: int,
    request: schemas.GenerateDescriptionRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"Generating job description for job ID: {id}")
    # 1. Retrieve job posting
    job_posting = db.query(models.JobPosting).filter(models.JobPosting.id == id).first()
    if not job_posting:
        logger.error(f"Job posting with ID {id} not found")
        raise HTTPException(status_code=404, detail="Job posting not found")

    # 2. Retrieve associated company info
    company = db.query(models.Company).filter(models.Company.id == job_posting.company_id).first()
    if not company:
        logger.error(f"Associated company for job ID {id} not found")
        raise HTTPException(status_code=404, detail="Associated company not found")

    # 3. Build prompt using job and tool info
    tools_str = ", ".join(request.required_tools)
    prompt = (
        f"Write a detailed job description for the position '{job_posting.title}' "
        f"at the company '{company.name}', which operates in the '{company.industry}' industry. "
        f"The candidate should be skilled in the following tools: {tools_str}."
    )

    # 4. Call OpenAI API
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    generated_description = response.choices[0].message.content.strip()
    generated_at = datetime.now(timezone.utc)

    # 5. Update DB with description
    job_posting.description = generated_description
    db.commit()
    db.refresh(job_posting)

    logger.info(f"Job description generated for job ID: {id}")
    # 6. Return response
    return schemas.GenerateDescriptionResponse(
        job_id=job_posting.id,
        description=generated_description,
        generated_at=generated_at
    )
    
