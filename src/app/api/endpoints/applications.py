from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from src.app.logging_config import logger  # Import the logger

router = APIRouter()


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


@router.post("/applications")
def post_application(application: Application):
    logger.info(f"Submitting application for {application.name}")
    applications.append(application)
    return {
  "status": "success",
  "message": f"Application submitted for {application.name}"
}

@router.get("/applications/")
def get_applications(company_name: str = None, candidate_email: str = None):
    logger.info(f"Fetching applications for {company_name} and {candidate_email}")
    filtered_applications = applications
    if company_name:
        logger.info(f"Filtering applications by company name: {company_name}")
        filtered_applications = [application for application in filtered_applications if application.company_name == company_name]
    if candidate_email:
        logger.info(f"Filtering applications by candidate email: {candidate_email}")
        filtered_applications = [application for application in filtered_applications if application.email == candidate_email]
    logger.info(f"Found {len(filtered_applications)} applications")
    return {
        "status": "success",
        "message": "Applications fetched successfully",
        "applications": filtered_applications
    }
@router.get("/applications/{candidate_id}")
def get_application(candidate_id: str):
    logger.info(f"Fetching application for candidate ID: {candidate_id}")
    for application in applications:
        if application.candidate_id == candidate_id:
            return {
                f"Application found for candidate ID: {candidate_id}",
                f"Application: {application}"
            }
    logger.info(f"Application for {candidate_id} not found")
    return {
        "status": "error",
        "message": f"Application not found for candidate ID: {candidate_id}"
    }

#accepts a json object with the following fields:
#email
#job_id
@router.put("/applications/{candidate_id}")
def update_application(candidate_id: str, application: Application):
    logger.info(f"Updating application for candidate ID: {candidate_id}")
    for app in applications:  # Use 'app' as the variable name for clarity
        if app.candidate_id == candidate_id:
            # Update the existing application with the new data
            app.email = application.email
            app.job_id = application.job_id
            app.company_name = application.company_name
            app.name = application.name  # If you want to update the name as well
            logger.info(f"Application for {candidate_id} successfully updated")
            return {
                f"Application for {candidate_id} successfully updated"
            }
    logger.info(f"Application for {candidate_id} not found")
    return {
        "status": "error",
        "message": f"Application not found for candidate ID: {candidate_id}"
    }


@router.patch("/applications/{candidate_id}")
def patch_application(candidate_id: str, application: ApplicationUpdate):
    logger.info(f"Patching application for candidate ID: {candidate_id}")
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
                logger.info(f"Application for {candidate_id} successfully updated. Updated fields: {', '.join(updated_fields)}")
                return {
                    "status": "success",
                    "message": f"Application for {candidate_id} successfully updated. Updated fields: {', '.join(updated_fields)}"
                }
            else:
                logger.info(f"No fields were updated for candidate ID: {candidate_id}")
                return {
                    "status": "info",
                    "message": "No fields were updated."
                }
    
    return {
        "status": "error",
        "message": f"Application not found for candidate ID: {candidate_id}"
    }

@router.delete("/applications/{candidate_id}")
def delete_application(candidate_id: str):
    for app in applications:
        if app.candidate_id == candidate_id:
            applications.remove(app)
            logger.info(f"Application for {candidate_id} successfully deleted")
            return {
                "status": "success",
                "message": f"Application for {candidate_id} successfully deleted"
            }
    logger.info(f"Application for {candidate_id} not found")
    return {
        "status": "error",
        "message": f"Application not found for candidate ID: {candidate_id}"
    }

