from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Application(BaseModel):
    candidate_id: str
    name: str
    email: str
    job_id: str
    company_name: str

class ApplicationUpdate(BaseModel):
    email: Optional[str] = None
    job_id: Optional[str] = None
       
applications = []

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
