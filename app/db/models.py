from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(MongoBaseModel):
    email: EmailStr
    full_name: str
    password_hash: Optional[str] = None
    profile_data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FilingMission(MongoBaseModel):
    user_id: PyObjectId
    financial_year: str = "2024-25"
    assessment_year: str = "2025-26"
    status: str = "INIT"  # INIT, EXTRACTING, REVIEW_REQUIRED, GENERATING, COMPLETED, FILED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaxDocument(MongoBaseModel):
    mission_id: PyObjectId
    doc_type: str  # FORM16_PART_A, FORM16_PART_B, AIS
    original_filename: str
    storage_path: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "UPLOADED"
    extraction_agent_id: Optional[str] = None

class ExtractedData(MongoBaseModel):
    mission_id: PyObjectId
    document_id: Optional[PyObjectId] = None
    doc_type: str
    
    # Raw data from AI
    raw_data: Dict[str, Any]
    
    # User verified/edited data
    verified_data: Optional[Dict[str, Any]] = None
    
    confidence_scores: Dict[str, float] = {}
    human_verification_status: str = "PENDING"  # PENDING, VERIFIED
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Filing(MongoBaseModel):
    mission_id: PyObjectId
    form_type: str  # ITR-1, ITR-2
    form_data: Dict[str, Any]
    computation_snapshot: Optional[Dict[str, Any]] = None
    version: int = 1
    is_final: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(MongoBaseModel):
    mission_id: PyObjectId
    target_collection: str
    target_id: PyObjectId
    field_path: str
    old_value: Any
    new_value: Any
    changed_by: Optional[PyObjectId] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
