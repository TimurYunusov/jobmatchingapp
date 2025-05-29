from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.app.logging_config import logger
from fastapi.responses import StreamingResponse
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage
import json
from typing import List
import os
from datetime import datetime

from src.app.db import get_db
from src.app.models import models
from src.app.schemas import schemas


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

def init_chat_model():
    return ChatOpenAI(
        model="gpt-4",
        streaming=True,
        temperature=0.2,
        max_tokens=500,
        model_kwargs={
            "top_p": 0.95,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5
        }
    )

@router.post("/{id}/description", response_model=schemas.GenerateDescriptionResponse)
async def generate_job_description(
    id: int,
    request: schemas.GenerateDescriptionRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"Generating job description for job ID: {id}")
    job_posting = db.query(models.JobPosting).filter(models.JobPosting.id == id).first()
    if not job_posting:
        logger.error(f"Job posting with ID {id} not found")
        raise HTTPException(status_code=404, detail="Job posting not found")

    company = db.query(models.Company).filter(models.Company.id == job_posting.company_id).first()
    if not company:
        logger.error(f"Associated company for job ID {id} not found")
        raise HTTPException(status_code=404, detail="Associated company not found")

    if not request.required_tools or not all(isinstance(tool, str) for tool in request.required_tools):
        raise HTTPException(status_code=400, detail="Invalid required_tools input")

    # Initialize the chat model
    chat = init_chat_model()
    
    # Create the prompt template
    system_template = """You are an expert job description writer. Create a detailed and professional job description 
    that follows the specified structure. Focus on clarity, professionalism, and attracting qualified candidates."""
    
    human_template = """Create a job description for the following position:
    
    Job Title: {title}
    Company: {company_name}
    Industry: {industry}
    Required Tools/Skills: {tools}
    Location Type: {location_type}
    Employment Type: {employment_type}
    
    Please structure the response with the following sections:
    - Overview
    - Responsibilities
    - Requirements
    - Qualifications
    - Benefits
    - Company Culture
    - Location Information
    - Compensation Information
    
    Make sure to highlight the required tools and skills throughout the description. If tools that listed is uknown, just don't mention it in description. 
    Guardrail:
    - Do not mention any tools that are not listed in the required tools.
    - Do not mention any tools that are not known to the user.
    - Do not mention any tools that are not known to the user. """
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template)
    ])
    
    # Format the prompt with the job details
    formatted_prompt = prompt.format_messages(
        title=job_posting.title,
        company_name=company.name,
        industry=company.industry,
        tools=", ".join(request.required_tools),
        location_type=job_posting.location_type,
        employment_type=job_posting.employment_type
    )

    try:
        # Get the complete response
        response = await chat.ainvoke(formatted_prompt)
        full_content = response.content

        # Parse the content into structured sections
        structured_response = schemas.StructuredJobDescription(
            title=job_posting.title,
            overview=full_content.split("Responsibilities")[0].strip(),
            responsibilities=[item.strip() for item in full_content.split("Responsibilities")[1].split("Requirements")[0].split("\n") if item.strip() and not item.strip().startswith(":")],
            requirements=[item.strip() for item in full_content.split("Requirements")[1].split("Qualifications")[0].split("\n") if item.strip() and not item.strip().startswith(":")],
            qualifications=[item.strip() for item in full_content.split("Qualifications")[1].split("Benefits")[0].split("\n") if item.strip() and not item.strip().startswith(":")],
            benefits=[item.strip() for item in full_content.split("Benefits")[1].split("Company Culture")[0].split("\n") if item.strip() and not item.strip().startswith(":")],
            company_culture=full_content.split("Company Culture")[1].split("Location Information")[0].strip() if "Company Culture" in full_content else None,
            location_info=full_content.split("Location Information")[1].split("Compensation Information")[0].strip() if "Location Information" in full_content else None,
            compensation_info=full_content.split("Compensation Information")[1].strip() if "Compensation Information" in full_content else None
        )

        return schemas.GenerateDescriptionResponse(
            job_id=id,
            description=full_content,  # Return the raw description as a string
            generated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error generating job description: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
