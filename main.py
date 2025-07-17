from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import json
import re
from datetime import datetime
import uuid
from enhanced_analysis import EnhancedContractAnalyzer
from enhanced_report_generator import EnhancedContractReportGenerator

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

# Initialize enhanced analyzer
analyzer = EnhancedContractAnalyzer()
report_generator = EnhancedContractReportGenerator()

async def analyze_contract_content(content: str) -> Dict[str, Any]:
    """Enhanced AI-powered contract analysis with Hugging Face integration"""
    
    # Use enhanced analyzer with AI
    risks, risk_score = await analyzer.analyze_risks_with_ai(content)
    compliance = analyzer.analyze_compliance(content)
    risk_level = analyzer.calculate_risk_level(risk_score)
    summary = analyzer.generate_summary(risks, compliance, risk_score)
    
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
        analysis_result = await analyze_contract_content(request.content)
        
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
    """Analyze uploaded contract file with enhanced parsing"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Read file content
    try:
        content = await file.read()
        
        # Use enhanced text extraction based on file type
        content_str = analyzer.extract_text_from_file(content, file.content_type)
        
        if content_str.startswith("Error"):
            raise HTTPException(status_code=400, detail=content_str)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
            # Perform enhanced analysis
        analysis_result = await analyze_contract_content(content_str)
    
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

@app.post("/generate-report")
async def generate_report(request: AnalysisRequest):
    """Generate PDF report for contract analysis"""
    
    try:
        # Perform analysis
        analysis_result = await analyze_contract_content(request.content)
        
        # Add metadata
        analysis_result["analysis_id"] = str(uuid.uuid4())
        analysis_result["filename"] = request.filename
        analysis_result["timestamp"] = datetime.now().isoformat()
        
        # Generate PDF report
        pdf_buffer = report_generator.generate_pdf_report(analysis_result, request.filename)
        
        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=contract_analysis_{analysis_result['analysis_id'][:8]}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@app.post("/analyze-file-report")
async def analyze_file_and_generate_report(file: UploadFile = File(...)):
    """Analyze uploaded file and generate PDF report"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        # Read and parse file
        content = await file.read()
        content_str = analyzer.extract_text_from_file(content, file.content_type)
        
        if content_str.startswith("Error"):
            raise HTTPException(status_code=400, detail=content_str)
        
        # Perform analysis
        analysis_result = await analyze_contract_content(content_str)
        
        # Add metadata
        analysis_result["analysis_id"] = str(uuid.uuid4())
        analysis_result["filename"] = file.filename
        analysis_result["timestamp"] = datetime.now().isoformat()
        
        # Generate PDF report
        pdf_buffer = report_generator.generate_pdf_report(analysis_result, file.filename)
        
        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=contract_analysis_{analysis_result['analysis_id'][:8]}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze and generate report: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 