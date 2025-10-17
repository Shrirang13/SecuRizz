from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class VulnerabilityPrediction(BaseModel):
    vulnerability: str
    probability: float


class AnalysisRequest(BaseModel):
    source_code: str
    contract_name: Optional[str] = None


class AnalysisResponse(BaseModel):
    contract_hash: str
    report_hash: str
    ipfs_cid: Optional[str] = None
    risk_score: float
    vulnerabilities: List[VulnerabilityPrediction]
    mitigation_strategies: Dict[str, str]
    created_at: datetime


class ContractCreate(BaseModel):
    source_code: str
    contract_name: Optional[str] = None


class ContractResponse(BaseModel):
    id: int
    contract_hash: str
    source_code: str
    created_at: datetime


class ReportResponse(BaseModel):
    id: int
    contract_id: int
    report_hash: str
    ipfs_cid: Optional[str]
    risk_score: float
    vulnerabilities: List[VulnerabilityPrediction]
    mitigation_strategies: Dict[str, str]
    created_at: datetime


class FeedbackCreate(BaseModel):
    report_id: int
    user_feedback: str
    accuracy_rating: int


class FeedbackResponse(BaseModel):
    id: int
    report_id: int
    user_feedback: str
    accuracy_rating: int
    created_at: datetime
