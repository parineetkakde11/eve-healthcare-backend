from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class CentreTest(Base):
    __tablename__ = "centre_tests"
    
    centre_id = Column(Integer, ForeignKey("diagnostic_centres.id", ondelete="CASCADE"), primary_key=True)
    test_id = Column(Integer, ForeignKey("diagnostic_tests.id", ondelete="CASCADE"), primary_key=True)

class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Many-to-many relationship
    tests = relationship("DiagnosticTest", secondary="centre_tests", backref="centres")

class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)