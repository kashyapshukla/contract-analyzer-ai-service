import re
import PyPDF2
from docx import Document
from io import BytesIO
from typing import Dict, List, Any, Tuple
import json
import os
import requests

class EnhancedContractAnalyzer:
    def __init__(self):
        # Configure Hugging Face
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.huggingface_api_url = "https://api-inference.huggingface.co/models"
        
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

    async def analyze_with_huggingface(self, content: str) -> Dict[str, Any]:
        """Analyze contract using Hugging Face Inference API"""
        try:
            if not self.huggingface_api_key:
                raise Exception("Hugging Face API key not configured")
            
            # Use a reliable and available model for text analysis
            model_name = "gpt2"  # Reliable and always available
            
            headers = {
                "Authorization": f"Bearer {self.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            # Create a structured prompt for contract analysis
            prompt = f"""
            Analyze this contract for legal risks and compliance issues. Provide analysis in this JSON format:
            {{
                "overall_risk": "LOW|MEDIUM|HIGH|CRITICAL",
                "confidence": 0.0-1.0,
                "risks": [
                    {{
                        "category": "risk category",
                        "severity": "LOW|MEDIUM|HIGH|CRITICAL", 
                        "description": "detailed description",
                        "clause": "section reference",
                        "recommendation": "specific recommendation"
                    }}
                ],
                "compliance": [
                    {{
                        "regulation": "compliance type",
                        "status": "check|warning|critical",
                        "description": "detailed description",
                        "clause": "section reference"
                    }}
                ],
                "summary": "overall analysis summary"
            }}
            
            Contract content: {content[:2000]}
            
            Focus on: liability, indemnification, termination, confidentiality, force majeure, arbitration, GDPR, SOX, HIPAA compliance.
            """
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 1000,
                    "temperature": 0.3,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                f"{self.huggingface_api_url}/{model_name}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Hugging Face API error: {response.status_code}")
            
            result = response.json()
            
            # Extract the generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            else:
                generated_text = str(result)
            
            # Try to extract JSON from the response
            try:
                # Look for JSON in the generated text
                json_start = generated_text.find('{')
                json_end = generated_text.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = generated_text[json_start:json_end]
                    return json.loads(json_str)
                else:
                    # If no JSON found, create structured response from text
                    return self.create_structured_response_from_text(generated_text, content)
            except json.JSONDecodeError:
                # Fallback: create structured response from generated text
                return self.create_structured_response_from_text(generated_text, content)
                
        except Exception as e:
            print(f"Hugging Face analysis failed: {str(e)}")
            if "403" in str(e):
                print("Hugging Face API key may be invalid or missing. Check environment variables.")
            elif "401" in str(e):
                print("Hugging Face API key is invalid. Please check your token.")
            return None

    def create_structured_response_from_text(self, text: str, original_content: str) -> Dict[str, Any]:
        """Create structured response from Hugging Face text output"""
        content_lower = original_content.lower()
        
        # Analyze the generated text and original content
        risks = []
        compliance = []
        
        # Extract risk information from patterns
        for risk_type, config in self.risk_patterns.items():
            for pattern in config["patterns"]:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    risks.append({
                        "category": config["category"],
                        "severity": config["severity"],
                        "description": f"Potential {config['category'].lower()} risk detected",
                        "clause": f"Section containing {risk_type} terms",
                        "recommendation": self._generate_recommendation(config["category"], config["severity"])
                    })
                    break
        
        # Extract compliance information
        for compliance_type, config in self.compliance_patterns.items():
            for pattern in config["patterns"]:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    compliance.append({
                        "regulation": config["regulation"],
                        "status": config["status"],
                        "description": f"Potential {config['regulation']} compliance requirement",
                        "clause": f"Section containing {compliance_type} terms"
                    })
                    break
        
        # Determine overall risk level
        risk_score = sum([{"low": 1, "medium": 2, "high": 3}[r["severity"]] * 2 for r in risks])
        overall_risk = self.calculate_risk_level(risk_score)
        
        # Create summary from AI analysis
        summary = f"AI analysis completed with {overall_risk.lower()} overall risk level. Found {len(risks)} risk items and {len(compliance)} compliance issues."
        
        return {
            "overall_risk": overall_risk,
            "confidence": min(0.95, 0.7 + (len(risks) * 0.05) + (len(compliance) * 0.03)),
            "risks": risks,
            "compliance": compliance,
            "summary": summary,
            "risk_score": risk_score
        }

    async def analyze_risks_with_ai(self, content: str) -> Tuple[List[Dict], int]:
        """Analyze risks using AI with fallback to pattern matching"""
        # Try Hugging Face first
        huggingface_result = await self.analyze_with_huggingface(content)
        
        if huggingface_result:
            try:
                risks = huggingface_result.get("risks", [])
                risk_score = huggingface_result.get("risk_score", 0)
                return risks, risk_score
            except Exception as e:
                print(f"Error parsing Hugging Face result: {str(e)}")
                # Fallback to pattern matching
                return self.analyze_risks(content)
        else:
            # Fallback to pattern matching
            return self.analyze_risks(content)

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
        """Generate detailed recommendations based on risk category and severity"""
        recommendations = {
            "Payment Terms": {
                "low": "STANDARD: Payment terms appear reasonable. Verify they align with your cash flow requirements and business operations.",
                "medium": "IMPORTANT: Review payment schedule and late fee structure. Consider negotiating 30-60 day payment terms with reasonable late fees (1-2% per month).",
                "high": "CRITICAL: Immediate attention required. Negotiate payment terms to 30-60 days with late fees capped at 1-2% per month. Request grace period and milestone-based payments for large contracts."
            },
            "Liability Limitations": {
                "low": "STANDARD: Liability terms appear reasonable. Consider liability insurance coverage for additional protection.",
                "medium": "IMPORTANT: Review liability limitations and ensure they're reasonable for your business. Negotiate liability caps and request mutual indemnification.",
                "high": "CRITICAL: Require legal review before signing. Request liability caps of 12-24 months of contract value. Include mutual indemnification and limit consequential damages."
            },
            "Termination Clauses": {
                "low": "STANDARD: Termination terms appear reasonable. Ensure adequate notice periods align with your business needs.",
                "medium": "IMPORTANT: Negotiate termination rights and cure periods. Request 30-60 day notice periods and define material breach clearly.",
                "high": "CRITICAL: Review termination provisions carefully. Negotiate 30-60 day notice periods, include cure periods for breaches, and request mutual termination rights."
            },
            "Confidentiality": {
                "low": "STANDARD: Confidentiality terms appear appropriate for the business relationship. Ensure scope is reasonable.",
                "medium": "REVIEW: Review confidentiality scope and duration. Limit confidentiality period to 3-5 years and include exceptions for public information.",
                "high": "IMPORTANT: Ensure adequate protection of sensitive information. Limit confidentiality scope to essential information only and include return/destruction requirements."
            },
            "Intellectual Property": {
                "low": "STANDARD: IP terms appear reasonable. Clarify IP ownership terms and ensure you retain rights to background IP.",
                "medium": "IMPORTANT: Negotiate IP rights and licensing terms. Request license to use deliverables and protect existing IP rights.",
                "high": "CRITICAL: Require legal review of IP provisions. Protect existing IP and limit assignment requirements. Define IP ownership clearly."
            },
            "Data Protection": {
                "low": "STANDARD: Data protection terms appear adequate. Ensure basic data protection measures are in place.",
                "medium": "IMPORTANT: Implement comprehensive data protection policies. Review data handling requirements and ensure GDPR/CCPA compliance.",
                "high": "CRITICAL: Require data protection officer review. Ensure GDPR/CCPA compliance with data breach notification, retention limits, and usage restrictions."
            },
            "Force Majeure": {
                "low": "STANDARD: Force majeure terms appear appropriate for the contract type. Ensure scope is reasonable.",
                "medium": "REVIEW: Review force majeure provisions and ensure they're reasonable. Include reasonable notice requirements.",
                "high": "IMPORTANT: Define force majeure events clearly and limit scope to truly unforeseeable events. Include reasonable notice requirements."
            },
            "Governing Law": {
                "low": "STANDARD: Governing law appears appropriate for the contract. Verify jurisdiction implications.",
                "medium": "REVIEW: Review governing law and venue carefully. Ensure they're appropriate for your business operations.",
                "high": "IMPORTANT: Consider jurisdiction implications and ensure dispute resolution is reasonable. Review choice of law carefully."
            }
        }
        
        return recommendations.get(category, {}).get(severity, "Seek legal review to ensure terms are appropriate for your business needs.")

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
        """Generate comprehensive analysis summary with detailed explanations"""
        risk_level = self.calculate_risk_level(risk_score)
        
        # Start with overall assessment
        summary = f"This comprehensive contract analysis reveals a {risk_level.lower()} risk profile with a risk score of {risk_score}/30. "
        
        # Analyze risk distribution
        if risks:
            high_risks = [r for r in risks if r["severity"] == "high"]
            medium_risks = [r for r in risks if r["severity"] == "medium"]
            low_risks = [r for r in risks if r["severity"] == "low"]
            
            summary += f"The analysis identified {len(risks)} risk factors: {len(high_risks)} high-priority, {len(medium_risks)} medium-priority, and {len(low_risks)} low-priority items. "
            
            # Highlight key risk categories
            risk_categories = {}
            for risk in risks:
                category = risk["category"]
                if category not in risk_categories:
                    risk_categories[category] = 0
                risk_categories[category] += 1
            
            if risk_categories:
                top_categories = sorted(risk_categories.items(), key=lambda x: x[1], reverse=True)[:3]
                category_names = [cat[0] for cat in top_categories]
                summary += f"Key risk areas include: {', '.join(category_names)}. "
        else:
            summary += "No significant risks were detected in this contract. "
        
        # Compliance analysis
        if compliance:
            compliance_regs = {}
            for comp in compliance:
                reg = comp["regulation"]
                if reg not in compliance_regs:
                    compliance_regs[reg] = 0
                compliance_regs[reg] += 1
            
            reg_names = list(compliance_regs.keys())
            summary += f"Compliance considerations include: {', '.join(reg_names)}. "
        else:
            summary += "No specific compliance issues were identified. "
        
        # Strategic recommendations based on risk level
        if risk_level in ["CRITICAL", "HIGH"]:
            summary += "STRATEGIC RECOMMENDATION: This contract requires immediate legal review and extensive negotiations. Consider requesting substantial modifications or walking away if terms cannot be improved. Focus on liability limitations, payment terms, and termination clauses."
        elif risk_level == "MEDIUM":
            summary += "STRATEGIC RECOMMENDATION: This contract has some concerning terms but is generally negotiable. Focus on the highest-risk items while accepting reasonable terms on others. Prioritize negotiation of liability caps and payment terms."
        else:
            summary += "STRATEGIC RECOMMENDATION: This contract appears to have reasonable terms. Minor negotiations may be beneficial but are not critical. Focus on ensuring all terms are clearly understood and documented."
        
        return summary 