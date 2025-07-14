from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import json
import re
from datetime import datetime
import uuid

app = FastAPI(
    title="AI Contract Risk Analyzer",
    description="AI-powered contract analysis and risk assessment service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    content: str
    filename: str

class RiskItem(BaseModel):
    category: str
    severity: str
    description: str
    clause: str
    recommendation: str

class ComplianceItem(BaseModel):
    regulation: str
    status: str
    description: str
    clause: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    filename: str
    risk_level: str
    risk_score: int
    risks: List[RiskItem]
    compliance: List[ComplianceItem]
    summary: str
    timestamp: str

def analyze_contract_content(content: str) -> Dict[str, Any]:
    """AI-powered contract analysis"""
    
    # Risk patterns to detect
    risk_patterns = {
        "payment_terms": {
            "patterns": [
                r"payment.*due.*\d+.*days",
                r"late.*payment.*\d+%",
                r"interest.*charge"
            ],
            "category": "Payment Terms",
            "severity": "medium"
        },
        "liability": {
            "patterns": [
                r"limitation.*liability",
                r"total.*liability.*not.*exceed",
                r"damages.*limited"
            ],
            "category": "Liability Limitations",
            "severity": "high"
        },
        "termination": {
            "patterns": [
                r"terminate.*\d+.*days.*notice",
                r"termination.*without.*cause",
                r"immediate.*termination"
            ],
            "category": "Termination Clauses",
            "severity": "medium"
        },
        "confidentiality": {
            "patterns": [
                r"confidential.*information",
                r"non-disclosure",
                r"trade.*secrets"
            ],
            "category": "Confidentiality",
            "severity": "low"
        },
        "intellectual_property": {
            "patterns": [
                r"intellectual.*property",
                r"copyright",
                r"patent",
                r"trademark"
            ],
            "category": "Intellectual Property",
            "severity": "high"
        }
    }
    
    # Compliance patterns
    compliance_patterns = {
        "gdpr": {
            "patterns": [r"personal.*data", r"data.*protection", r"privacy"],
            "regulation": "GDPR",
            "status": "check"
        },
        "sox": {
            "patterns": [r"financial.*reporting", r"internal.*controls", r"audit"],
            "regulation": "SOX",
            "status": "check"
        },
        "hipaa": {
            "patterns": [r"health.*information", r"medical.*records", r"phi"],
            "regulation": "HIPAA",
            "status": "check"
        }
    }
    
    # Analyze risks
    risks = []
    risk_score = 0
    
    for risk_type, config in risk_patterns.items():
        for pattern in config["patterns"]:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                clause = match.group(0)
                context_start = max(0, match.start() - 50)
                context_end = min(len(content), match.end() + 50)
                full_clause = content[context_start:context_end]
                
                severity_score = {"low": 1, "medium": 2, "high": 3}[config["severity"]]
                risk_score += severity_score
                
                risks.append({
                    "category": config["category"],
                    "severity": config["severity"],
                    "description": f"Potential {config['category'].lower()} risk detected",
                    "clause": full_clause.strip(),
                    "recommendation": f"Review {config['category'].lower()} terms with legal counsel"
                })
    
    # Analyze compliance
    compliance = []
    
    for compliance_type, config in compliance_patterns.items():
        for pattern in config["patterns"]:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                clause = match.group(0)
                context_start = max(0, match.start() - 50)
                context_end = min(len(content), match.end() + 50)
                full_clause = content[context_start:context_end]
                
                compliance.append({
                    "regulation": config["regulation"],
                    "status": config["status"],
                    "description": f"Potential {config['regulation']} compliance requirement",
                    "clause": full_clause.strip()
                })
    
    # Determine overall risk level
    if risk_score >= 10:
        risk_level = "HIGH"
    elif risk_score >= 5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Generate summary
    summary = f"Contract analysis completed. Risk level: {risk_level}. "
    summary += f"Found {len(risks)} potential risk items and {len(compliance)} compliance considerations. "
    
    if risk_score > 0:
        summary += "Recommend legal review before signing."
    else:
        summary += "Contract appears to have standard terms."
    
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risks": risks,
        "compliance": compliance,
        "summary": summary
    }

@app.get("/")
async def root():
    return {"message": "AI Contract Risk Analyzer API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_contract(request: AnalysisRequest):
    """Analyze contract content for risks and compliance"""
    
    try:
        # Perform AI analysis
        analysis_result = analyze_contract_content(request.content)
        
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            filename=request.filename,
            risk_level=analysis_result["risk_level"],
            risk_score=analysis_result["risk_score"],
            risks=analysis_result["risks"],
            compliance=analysis_result["compliance"],
            summary=analysis_result["summary"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    """Analyze uploaded contract file"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Read file content
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # Perform analysis
    analysis_result = analyze_contract_content(content_str)
    
    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    return {
        "analysis_id": analysis_id,
        "filename": file.filename,
        "risk_level": analysis_result["risk_level"],
        "risk_score": analysis_result["risk_score"],
        "risks": analysis_result["risks"],
        "compliance": analysis_result["compliance"],
        "summary": analysis_result["summary"],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 