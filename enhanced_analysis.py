import re
import PyPDF2
from docx import Document
from io import BytesIO
from typing import Dict, List, Any, Tuple
import json

class EnhancedContractAnalyzer:
    def __init__(self):
        # Enhanced risk patterns with more sophisticated detection
        self.risk_patterns = {
            "payment_terms": {
                "patterns": [
                    r"payment.*due.*(\d+).*days",
                    r"late.*payment.*(\d+%)",
                    r"interest.*charge.*(\d+%)",
                    r"penalty.*(\d+%)",
                    r"default.*rate.*(\d+%)"
                ],
                "category": "Payment Terms",
                "severity": "medium",
                "weight": 2
            },
            "liability": {
                "patterns": [
                    r"limitation.*liability",
                    r"total.*liability.*not.*exceed.*(\$[\d,]+)",
                    r"damages.*limited.*(\$[\d,]+)",
                    r"exclude.*consequential.*damages",
                    r"indemnification.*unlimited"
                ],
                "category": "Liability Limitations",
                "severity": "high",
                "weight": 3
            },
            "termination": {
                "patterns": [
                    r"terminate.*(\d+).*days.*notice",
                    r"termination.*without.*cause",
                    r"immediate.*termination",
                    r"breach.*(\d+).*days.*cure",
                    r"material.*breach"
                ],
                "category": "Termination Clauses",
                "severity": "medium",
                "weight": 2
            },
            "confidentiality": {
                "patterns": [
                    r"confidential.*information",
                    r"non-disclosure.*(\d+).*years",
                    r"trade.*secrets",
                    r"proprietary.*information",
                    r"return.*confidential.*information"
                ],
                "category": "Confidentiality",
                "severity": "low",
                "weight": 1
            },
            "intellectual_property": {
                "patterns": [
                    r"intellectual.*property",
                    r"copyright.*assignment",
                    r"patent.*rights",
                    r"trademark.*usage",
                    r"work.*for.*hire"
                ],
                "category": "Intellectual Property",
                "severity": "high",
                "weight": 3
            },
            "data_protection": {
                "patterns": [
                    r"personal.*data",
                    r"data.*protection",
                    r"privacy.*policy",
                    r"gdpr.*compliance",
                    r"data.*breach.*notification"
                ],
                "category": "Data Protection",
                "severity": "high",
                "weight": 3
            },
            "force_majeure": {
                "patterns": [
                    r"force.*majeure",
                    r"act.*of.*god",
                    r"unforeseen.*circumstances",
                    r"beyond.*reasonable.*control"
                ],
                "category": "Force Majeure",
                "severity": "low",
                "weight": 1
            },
            "governing_law": {
                "patterns": [
                    r"governing.*law.*([A-Za-z\s]+)",
                    r"jurisdiction.*([A-Za-z\s]+)",
                    r"venue.*([A-Za-z\s]+)",
                    r"dispute.*resolution"
                ],
                "category": "Governing Law",
                "severity": "medium",
                "weight": 2
            }
        }
        
        # Enhanced compliance patterns
        self.compliance_patterns = {
            "gdpr": {
                "patterns": [
                    r"personal.*data.*processing",
                    r"data.*subject.*rights",
                    r"data.*protection.*officer",
                    r"privacy.*impact.*assessment",
                    r"right.*to.*erasure"
                ],
                "regulation": "GDPR",
                "status": "check",
                "weight": 3
            },
            "sox": {
                "patterns": [
                    r"financial.*reporting",
                    r"internal.*controls",
                    r"audit.*committee",
                    r"material.*weakness",
                    r"disclosure.*controls"
                ],
                "regulation": "SOX",
                "status": "check",
                "weight": 3
            },
            "hipaa": {
                "patterns": [
                    r"health.*information",
                    r"medical.*records",
                    r"phi.*protected.*health",
                    r"privacy.*rule",
                    r"security.*rule"
                ],
                "regulation": "HIPAA",
                "status": "check",
                "weight": 3
            },
            "ccpa": {
                "patterns": [
                    r"california.*privacy",
                    r"consumer.*privacy.*act",
                    r"right.*to.*know",
                    r"right.*to.*delete",
                    r"opt.*out.*sale"
                ],
                "regulation": "CCPA",
                "status": "check",
                "weight": 2
            }
        }

    def parse_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF files"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"

    def parse_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX files"""
        try:
            doc = Document(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error parsing DOCX: {str(e)}"

    def parse_text(self, file_content: bytes) -> str:
        """Extract text from plain text files"""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1')
            except:
                return "Error decoding text file"

    def extract_text_from_file(self, file_content: bytes, file_type: str) -> str:
        """Extract text from different file types"""
        if file_type == "application/pdf":
            return self.parse_pdf(file_content)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self.parse_docx(file_content)
        elif file_type == "text/plain":
            return self.parse_text(file_content)
        else:
            return "Unsupported file type"

    def analyze_risks(self, content: str) -> Tuple[List[Dict], int]:
        """Enhanced risk analysis with sophisticated detection"""
        risks = []
        total_risk_score = 0
        
        for risk_type, config in self.risk_patterns.items():
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Extract context around the match
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()
                    
                    # Calculate risk score based on pattern weight and severity
                    severity_score = {"low": 1, "medium": 2, "high": 3}[config["severity"]]
                    pattern_score = config["weight"] * severity_score
                    total_risk_score += pattern_score
                    
                    # Extract monetary amounts if present
                    monetary_match = re.search(r'\$[\d,]+', match.group(0))
                    monetary_value = monetary_match.group(0) if monetary_match else None
                    
                    risks.append({
                        "category": config["category"],
                        "severity": config["severity"],
                        "description": f"Potential {config['category'].lower()} risk detected",
                        "clause": context,
                        "pattern_matched": match.group(0),
                        "monetary_value": monetary_value,
                        "risk_score": pattern_score,
                        "recommendation": self._generate_recommendation(config["category"], config["severity"])
                    })
        
        return risks, total_risk_score

    def analyze_compliance(self, content: str) -> List[Dict]:
        """Enhanced compliance analysis"""
        compliance_issues = []
        
        for compliance_type, config in self.compliance_patterns.items():
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()
                    
                    compliance_issues.append({
                        "regulation": config["regulation"],
                        "status": config["status"],
                        "description": f"Potential {config['regulation']} compliance requirement",
                        "clause": context,
                        "pattern_matched": match.group(0),
                        "weight": config["weight"],
                        "recommendation": f"Review {config['regulation']} compliance requirements with legal counsel"
                    })
        
        return compliance_issues

    def _generate_recommendation(self, category: str, severity: str) -> str:
        """Generate specific recommendations based on risk category and severity"""
        recommendations = {
            "Payment Terms": {
                "low": "Review payment terms for reasonableness",
                "medium": "Negotiate more favorable payment terms",
                "high": "Seek legal review of payment terms immediately"
            },
            "Liability Limitations": {
                "low": "Consider liability insurance coverage",
                "medium": "Negotiate liability caps and exclusions",
                "high": "Require legal review before signing"
            },
            "Termination Clauses": {
                "low": "Ensure adequate notice periods",
                "medium": "Negotiate termination rights and cure periods",
                "high": "Review termination provisions carefully"
            },
            "Confidentiality": {
                "low": "Standard confidentiality terms",
                "medium": "Review confidentiality scope and duration",
                "high": "Ensure adequate protection of sensitive information"
            },
            "Intellectual Property": {
                "low": "Clarify IP ownership terms",
                "medium": "Negotiate IP rights and licensing terms",
                "high": "Require legal review of IP provisions"
            },
            "Data Protection": {
                "low": "Ensure basic data protection measures",
                "medium": "Implement comprehensive data protection policies",
                "high": "Require data protection officer review"
            }
        }
        
        return recommendations.get(category, {}).get(severity, "Seek legal review")

    def calculate_risk_level(self, risk_score: int) -> str:
        """Calculate overall risk level based on score"""
        if risk_score >= 20:
            return "CRITICAL"
        elif risk_score >= 15:
            return "HIGH"
        elif risk_score >= 10:
            return "MEDIUM"
        elif risk_score >= 5:
            return "LOW"
        else:
            return "MINIMAL"

    def generate_summary(self, risks: List[Dict], compliance: List[Dict], risk_score: int) -> str:
        """Generate comprehensive analysis summary"""
        risk_level = self.calculate_risk_level(risk_score)
        
        summary = f"Contract analysis completed. Overall risk level: {risk_level}. "
        summary += f"Risk score: {risk_score}/30. "
        
        if risks:
            high_risks = [r for r in risks if r["severity"] == "high"]
            medium_risks = [r for r in risks if r["severity"] == "medium"]
            
            summary += f"Found {len(risks)} risk items ({len(high_risks)} high, {len(medium_risks)} medium). "
        else:
            summary += "No significant risks detected. "
        
        if compliance:
            summary += f"Identified {len(compliance)} compliance considerations. "
        
        if risk_score >= 15:
            summary += "RECOMMENDATION: Legal review required before signing."
        elif risk_score >= 10:
            summary += "RECOMMENDATION: Consider legal review for high-risk terms."
        else:
            summary += "Contract appears to have standard terms."
        
        return summary 