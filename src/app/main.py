from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.api.endpoints import applications

from .api.endpoints import companies, jobs

app = FastAPI(title="Job Board API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(jobs.router, prefix="/job-postings", tags=["job-postings"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Job Board API designed and developed by the Timur at Job Board"} 