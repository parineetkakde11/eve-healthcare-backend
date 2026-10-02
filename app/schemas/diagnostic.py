from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# --- Diagnostic Test Schemas ---
class DiagnosticTestCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal

class DiagnosticTestResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Diagnostic Centre Schemas ---
class DiagnosticCentreCreate(BaseModel):
    name: str
    location: str
    test_ids: List[int] = []  # List of test IDs this centre offers

class DiagnosticCentreResponse(BaseModel):
    id: int
    name: str
    location: str
    created_at: datetime
    tests: List[DiagnosticTestResponse] = []  # Nested list of available tests

    model_config = ConfigDict(from_attributes=True)