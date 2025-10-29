from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import hashlib
import json
import os
from datetime import datetime

from .database import get_db, create_tables, Contract, AuditReport, Feedback
from .models import (
    AnalysisRequest, AnalysisResponse, ContractCreate, ContractResponse,
    ReportResponse, FeedbackCreate, FeedbackResponse, VulnerabilityPrediction
)
from .ipfs_client import ipfs_client
from .ml_client import ml_client
from .solana_client import solana_client
from .security import security_manager, require_auth, rate_limit_check, validate_input
from .cross_chain import cross_chain_manager

app = FastAPI(title="SecuRizz API", version="1.0.0")

# Get CORS origins from environment
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
if cors_origins == ["*"]:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    create_tables()


@app.get("/")
async def root():
    return {"message": "SecuRizz API - Smart Contract Vulnerability Auditor"}


@app.post("/analyze", response_model=AnalysisResponse)
@rate_limit_check("user_id")
@validate_input(["source_code", "contract_name"])
async def analyze_contract(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    try:
        ml_result = ml_client.analyze_contract(request.source_code)
        
        vulnerabilities = [
            VulnerabilityPrediction(
                vulnerability=vuln["vulnerability"],
                probability=vuln["probability"]
            )
            for vuln in ml_result["predictions"]
            if vuln["probability"] > 0.5
        ]
        
        mitigation_strategies = {}
        for vuln in vulnerabilities:
            if vuln.vulnerability == "reentrancy":
                mitigation_strategies[vuln.vulnerability] = "Use checks-effects-interactions pattern and reentrancy guards"
            elif vuln.vulnerability == "integer_overflow":
                mitigation_strategies[vuln.vulnerability] = "Use SafeMath library or Solidity 0.8+ checked arithmetic"
            elif vuln.vulnerability == "access_control":
                mitigation_strategies[vuln.vulnerability] = "Implement proper role-based access control and onlyOwner modifiers"
            elif vuln.vulnerability == "tx_origin":
                mitigation_strategies[vuln.vulnerability] = "Use msg.sender instead of tx.origin for authentication"
            elif vuln.vulnerability == "timestamp_dependency":
                mitigation_strategies[vuln.vulnerability] = "Avoid using block.timestamp for critical logic"
            else:
                mitigation_strategies[vuln.vulnerability] = "Review contract logic and implement appropriate security measures"
        
        report_data = {
            "contract_hash": ml_result["contract_hash"],
            "source_code": request.source_code,
            "vulnerabilities": [v.dict() for v in vulnerabilities],
            "mitigation_strategies": mitigation_strategies,
            "risk_score": ml_result["risk_score"],
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "contract_name": request.contract_name
        }
        
        # Store on IPFS
        ipfs_cid = ipfs_client.pin_json(report_data, f"audit_report_{ml_result['contract_hash'][:8]}")
        
        # Submit to Solana blockchain
        solana_tx = await solana_client.submit_audit_proof(
            ml_result["contract_hash"],
            hashlib.sha256(json.dumps(report_data, sort_keys=True).encode()).hexdigest(),
            ipfs_cid,
            int(ml_result["risk_score"] * 100),
            int((1 - ml_result["risk_score"]) * 100),
            "mock_contract_address"
        )
        
        report_content = json.dumps(report_data, sort_keys=True)
        report_hash = hashlib.sha256(report_content.encode()).hexdigest()
        
        contract = db.query(Contract).filter(Contract.contract_hash == ml_result["contract_hash"]).first()
        if not contract:
            contract = Contract(
                contract_hash=ml_result["contract_hash"],
                source_code=request.source_code
            )
            db.add(contract)
            db.commit()
            db.refresh(contract)
        
        audit_report = AuditReport(
            contract_id=contract.id,
            report_hash=report_hash,
            ipfs_cid=ipfs_cid,
            risk_score=ml_result["risk_score"],
            vulnerabilities=json.dumps([v.dict() for v in vulnerabilities]),
            mitigation_strategies=json.dumps(mitigation_strategies)
        )
        db.add(audit_report)
        db.commit()
        db.refresh(audit_report)
        
        return AnalysisResponse(
            contract_hash=ml_result["contract_hash"],
            report_hash=report_hash,
            ipfs_cid=ipfs_cid,
            risk_score=ml_result["risk_score"],
            vulnerabilities=vulnerabilities,
            mitigation_strategies=mitigation_strategies,
            created_at=audit_report.created_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/contracts", response_model=List[ContractResponse])
async def get_contracts(db: Session = Depends(get_db)):
    contracts = db.query(Contract).all()
    return [
        ContractResponse(
            id=c.id,
            contract_hash=c.contract_hash,
            source_code=c.source_code,
            created_at=c.created_at
        )
        for c in contracts
    ]


@app.get("/reports", response_model=List[ReportResponse])
async def get_reports(db: Session = Depends(get_db)):
    reports = db.query(AuditReport).all()
    return [
        ReportResponse(
            id=r.id,
            contract_id=r.contract_id,
            report_hash=r.report_hash,
            ipfs_cid=r.ipfs_cid,
            risk_score=r.risk_score,
            vulnerabilities=json.loads(r.vulnerabilities) if r.vulnerabilities else [],
            mitigation_strategies=json.loads(r.mitigation_strategies) if r.mitigation_strategies else {},
            created_at=r.created_at
        )
        for r in reports
    ]


@app.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(AuditReport).filter(AuditReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return ReportResponse(
        id=report.id,
        contract_id=report.contract_id,
        report_hash=report.report_hash,
        ipfs_cid=report.ipfs_cid,
        risk_score=report.risk_score,
        vulnerabilities=json.loads(report.vulnerabilities) if report.vulnerabilities else [],
        mitigation_strategies=json.loads(report.mitigation_strategies) if report.mitigation_strategies else {},
        created_at=report.created_at
    )


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    report = db.query(AuditReport).filter(AuditReport.id == feedback.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    feedback_entry = Feedback(
        report_id=feedback.report_id,
        user_feedback=feedback.user_feedback,
        accuracy_rating=feedback.accuracy_rating
    )
    db.add(feedback_entry)
    db.commit()
    db.refresh(feedback_entry)
    
    return FeedbackResponse(
        id=feedback_entry.id,
        report_id=feedback_entry.report_id,
        user_feedback=feedback_entry.user_feedback,
        accuracy_rating=feedback_entry.accuracy_rating,
        created_at=feedback_entry.created_at
    )


@app.get("/verify/{contract_address}")
async def verify_contract_on_chain(contract_address: str):
    """
    Verify contract audit status on Solana blockchain
    """
    try:
        # This would integrate with Solana RPC to query the program
        # For now, return a mock response
        return {
            "contract_address": contract_address,
            "audit_status": "verified",
            "audit_score": 85,
            "risk_score": 0.15,
            "timestamp": datetime.utcnow().isoformat(),
            "explorer_link": f"https://explorer.solana.com/address/{contract_address}",
            "verified": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
