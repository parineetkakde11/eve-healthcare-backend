from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.diagnostic import DiagnosticCentre, DiagnosticTest
from app.schemas.diagnostic import (
    DiagnosticCentreCreate, DiagnosticCentreResponse,
    DiagnosticTestCreate, DiagnosticTestResponse
)
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["Diagnostic Centres & Tests"])

@router.post("/tests", response_model=DiagnosticTestResponse, status_code=status.HTTP_201_CREATED)
def create_test(
    test_in: DiagnosticTestCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Ensure price is positive
    if test_in.price <= 0:
        raise HTTPException(status_code=422, detail="Price must be greater than zero.")
        
    test_exists = db.query(DiagnosticTest).filter(DiagnosticTest.name == test_in.name).first()
    if test_exists:
        raise HTTPException(status_code=409, detail="Test with this name already exists.")

    new_test = DiagnosticTest(**test_in.model_dump())
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return new_test

@router.get("/tests", response_model=List[DiagnosticTestResponse])
def get_tests(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(DiagnosticTest).offset(skip).limit(limit).all()

@router.post("/centres", response_model=DiagnosticCentreResponse, status_code=status.HTTP_201_CREATED)
def create_centre(
    centre_in: DiagnosticCentreCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the actual test objects based on provided IDs
    tests = db.query(DiagnosticTest).filter(DiagnosticTest.id.in_(centre_in.test_ids)).all()
    if len(tests) != len(centre_in.test_ids):
        raise HTTPException(status_code=400, detail="One or more test_ids are invalid.")

    new_centre = DiagnosticCentre(
        name=centre_in.name,
        location=centre_in.location,
        tests=tests
    )
    db.add(new_centre)
    db.commit()
    db.refresh(new_centre)
    return new_centre

@router.get("/centres", response_model=List[DiagnosticCentreResponse])
def get_centres(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(DiagnosticCentre).offset(skip).limit(limit).all()