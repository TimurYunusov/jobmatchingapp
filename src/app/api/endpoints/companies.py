from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.app.logging_config import logger  # Import the logger

from src.app.db import get_db
from src.app.models import models
from src.app.schemas import schemas

router = APIRouter()


#Company Endpoints:
@router.post("/add_company", response_model=schemas.CompanyResponse)
def add_company(
    company: schemas.CompanyCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Adding company: {company.name}")
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

# Endpoint to GET all companies
@router.get("/get_companies", response_model=list[schemas.CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    companies = db.query(models.Company).all()
    return companies

# ---------------- READ (GET ONE) ----------------
@router.get("/companies/{company_id}", response_model=schemas.CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    logger.info(f"Company retrieved: {company.name}")
    return company

# ---------------- UPDATE ----------------
@router.put("/companies/{company_id}", response_model=schemas.CompanyResponse)
def update_company(
    company_id: int, 
    company_update: schemas.CompanyCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Updating company with ID: {company_id}")
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for key, value in company_update.dict().items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)
    logger.info(f"Company updated: {company.name}")
    return company

# ---------------- DELETE ----------------
@router.delete("/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting company with ID: {company_id}")
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db.delete(company)
    db.commit()
    logger.info(f"Company with ID {company_id} deleted")
    return {"status": "success", "detail": f"Company {company_id} deleted"}