from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Any
import json
import re

class EnhancedContractReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self._setup_negotiation_guidance()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.grey,
            fontName='Helvetica'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=8,
            backColor=colors.lightblue
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Risk item style
        self.styles.add(ParagraphStyle(
            name='RiskItem',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            alignment=TA_JUSTIFY
        ))
        
        # Negotiation point style
        self.styles.add(ParagraphStyle(
            name='NegotiationPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=25,
            alignment=TA_JUSTIFY,
            backColor=colors.lightyellow,
            borderWidth=1,
            borderColor=colors.orange,
            borderPadding=5
        ))
        
        # Summary style
        self.styles.add(ParagraphStyle(
            name='Summary',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Warning style
        self.styles.add(ParagraphStyle(
            name='Warning',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            textColor=colors.red,
            fontName='Helvetica-Bold'
        ))
        
        # Success style
        self.styles.add(ParagraphStyle(
            name='Success',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            textColor=colors.green,
            fontName='Helvetica-Bold'
        ))

    def _setup_negotiation_guidance(self):
        """Setup negotiation guidance for different contract terms"""
        self.negotiation_guidance = {
            "Payment Terms": {
                "explanation": "Payment terms define when and how payments are made, including late fees and penalties.",
                "red_flags": [
                    "Payment due immediately upon signing",
                    "Late fees exceeding 2% per month",
                    "No grace period for payments",
                    "Unreasonable payment schedules"
                ],
                "negotiation_points": [
                    "Request 30-60 day payment terms",
                    "Negotiate late fees to 1-2% per month",
                    "Include grace period of 5-10 days",
                    "Request milestone-based payments for large contracts"
                ],
                "market_standard": "Standard payment terms are typically 30-60 days with 1-2% late fees."
            },
            "Liability Limitations": {
                "explanation": "Liability clauses limit the amount of damages one party can claim from the other.",
                "red_flags": [
                    "Unlimited liability exposure",
                    "No liability caps",
                    "Exclusion of consequential damages",
                    "One-sided indemnification"
                ],
                "negotiation_points": [
                    "Request liability caps (e.g., 12 months of fees)",
                    "Include mutual indemnification",
                    "Limit consequential damages",
                    "Request insurance requirements"
                ],
                "market_standard": "Typical liability caps are 12-24 months of contract value."
            },
            "Termination Clauses": {
                "explanation": "Termination clauses define how and when the contract can be ended.",
                "red_flags": [
                    "Immediate termination without cause",
                    "No cure period for breaches",
                    "Unilateral termination rights",
                    "Excessive notice periods"
                ],
                "negotiation_points": [
                    "Request 30-60 day notice period",
                    "Include cure periods for breaches",
                    "Request mutual termination rights",
                    "Define material breach clearly"
                ],
                "market_standard": "Standard notice periods are 30-60 days with cure periods for breaches."
            },
            "Confidentiality": {
                "explanation": "Confidentiality clauses protect sensitive information shared during the contract.",
                "red_flags": [
                    "Unlimited confidentiality period",
                    "No exceptions for public information",
                    "Overly broad definition of confidential information",
                    "No return/destruction requirements"
                ],
                "negotiation_points": [
                    "Limit confidentiality period to 3-5 years",
                    "Include exceptions for public information",
                    "Define confidential information narrowly",
                    "Request return/destruction of materials"
                ],
                "market_standard": "Standard confidentiality periods are 3-5 years after contract termination."
            },
            "Intellectual Property": {
                "explanation": "IP clauses define ownership and usage rights for intellectual property.",
                "red_flags": [
                    "Assignment of all IP to one party",
                    "No license to use background IP",
                    "Unlimited use of deliverables",
                    "No protection of existing IP"
                ],
                "negotiation_points": [
                    "Retain ownership of background IP",
                    "Request license to use deliverables",
                    "Limit use of deliverables",
                    "Protect existing IP rights"
                ],
                "market_standard": "Each party typically retains ownership of their background IP."
            },
            "Data Protection": {
                "explanation": "Data protection clauses ensure compliance with privacy regulations.",
                "red_flags": [
                    "No data protection requirements",
                    "Unlimited data usage rights",
                    "No data breach notification",
                    "No data retention limits"
                ],
                "negotiation_points": [
                    "Include GDPR/CCPA compliance",
                    "Limit data usage to contract purposes",
                    "Request data breach notification",
                    "Set data retention limits"
                ],
                "market_standard": "Data should be used only for contract purposes and retained for limited periods."
            }
        }

    def generate_pdf_report(self, analysis_data: Dict[str, Any], filename: str) -> BytesIO:
        """Generate a comprehensive PDF report with detailed analysis"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        
        story = []
        
        # Title page
        story.extend(self._create_title_page(analysis_data, filename))
        story.append(PageBreak())
        
        # Table of Contents (simplified)
        story.extend(self._create_table_of_contents())
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary(analysis_data))
        story.append(PageBreak())
        
        # Contract Overview
        story.extend(self._create_contract_overview(analysis_data, filename))
        story.append(PageBreak())
        
        # Detailed Risk Analysis
        story.extend(self._create_detailed_risk_analysis(analysis_data))
        story.append(PageBreak())
        
        # Compliance Analysis
        story.extend(self._create_compliance_analysis(analysis_data))
        story.append(PageBreak())
        
        # Negotiation Strategy
        story.extend(self._create_negotiation_strategy(analysis_data))
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self._create_recommendations(analysis_data))
        story.append(PageBreak())
        
        # Technical Details
        story.extend(self._create_technical_details(analysis_data))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    def _create_title_page(self, analysis_data: Dict[str, Any], filename: str) -> List:
        """Create the title page"""
        story = []
        
        # Title
        title = Paragraph("Contract Risk Analysis & Negotiation Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Subtitle
        subtitle = Paragraph("Comprehensive Legal Analysis & Strategic Recommendations", self.styles['Subtitle'])
        story.append(subtitle)
        story.append(Spacer(1, 40))
        
        # Document info
        doc_info = [
            ["Document Analyzed:", filename],
            ["Analysis Date:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ["Analysis ID:", analysis_data.get('analysis_id', 'N/A')],
            ["Risk Level:", f"<b>{analysis_data.get('risk_level', 'UNKNOWN')}</b>"],
            ["Risk Score:", f"<b>{analysis_data.get('risk_score', 0)}/30</b>"],
            ["Total Risks Found:", f"<b>{len(analysis_data.get('risks', []))}</b>"],
            ["Compliance Issues:", f"<b>{len(analysis_data.get('compliance', []))}</b>"]
        ]
        
        doc_table = Table(doc_info, colWidths=[2.5*inch, 4*inch])
        doc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(doc_table)
        story.append(Spacer(1, 30))
        
        # Risk level indicator with color
        risk_level = analysis_data.get('risk_level', 'UNKNOWN')
        risk_color = self._get_risk_color(risk_level)
        risk_description = self._get_risk_description(risk_level)
        
        risk_indicator = Paragraph(
            f"<b>Overall Risk Assessment:</b> <font color='{risk_color}'>{risk_level}</font><br/>"
            f"<i>{risk_description}</i>",
            self.styles['Summary']
        )
        story.append(risk_indicator)
        
        return story

    def _create_table_of_contents(self) -> List:
        """Create table of contents"""
        story = []
        
        story.append(Paragraph("Table of Contents", self.styles['SectionHeader']))
        story.append(Spacer(1, 20))
        
        toc_items = [
            "Executive Summary",
            "Contract Overview",
            "Detailed Risk Analysis",
            "Compliance Analysis", 
            "Negotiation Strategy",
            "Recommendations",
            "Technical Details"
        ]
        
        for i, item in enumerate(toc_items, 1):
            toc_item = Paragraph(f"{i}. {item}", self.styles['Summary'])
            story.append(toc_item)
            story.append(Spacer(1, 5))
        
        return story

    def _create_executive_summary(self, analysis_data: Dict[str, Any]) -> List:
        """Create comprehensive executive summary"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Spacer(1, 15))
        
        # Overall assessment
        risk_level = analysis_data.get('risk_level', 'UNKNOWN')
        risk_score = analysis_data.get('risk_score', 0)
        
        summary_text = f"""
        This comprehensive contract analysis reveals a <b>{risk_level.lower()}</b> risk profile with a risk score of <b>{risk_score}/30</b>. 
        The analysis identified {len(analysis_data.get('risks', []))} risk factors and {len(analysis_data.get('compliance', []))} compliance considerations.
        """
        
        story.append(Paragraph(summary_text, self.styles['Summary']))
        story.append(Spacer(1, 15))
        
        # Key findings
        story.append(Paragraph("Key Findings", self.styles['SubsectionHeader']))
        
        risks = analysis_data.get('risks', [])
        high_risks = [r for r in risks if r.get('severity') == 'high']
        medium_risks = [r for r in risks if r.get('severity') == 'medium']
        low_risks = [r for r in risks if r.get('severity') == 'low']
        
        findings_data = [
            ["Risk Category", "Count", "Priority", "Action Required"],
            ["High Risk Items", str(len(high_risks)), "Critical", "Immediate Review"],
            ["Medium Risk Items", str(len(medium_risks)), "Moderate", "Negotiate"],
            ["Low Risk Items", str(len(low_risks)), "Minor", "Monitor"],
            ["Compliance Issues", str(len(analysis_data.get('compliance', []))), "Review", "Verify"]
        ]
        
        findings_table = Table(findings_data, colWidths=[2*inch, 0.8*inch, 1.2*inch, 2*inch])
        findings_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightcoral),
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightyellow),
            ('BACKGROUND', (0, 3), (-1, 3), colors.lightgreen),
        ]))
        
        story.append(findings_table)
        story.append(Spacer(1, 15))
        
        # Top recommendations
        story.append(Paragraph("Top Recommendations", self.styles['SubsectionHeader']))
        
        if high_risks:
            story.append(Paragraph(
                f"⚠️ <b>Critical:</b> Address {len(high_risks)} high-risk items before signing",
                self.styles['Warning']
            ))
        
        if medium_risks:
            story.append(Paragraph(
                f"⚖️ <b>Negotiate:</b> Review {len(medium_risks)} medium-risk terms",
                self.styles['Summary']
            ))
        
        if risk_score < 10:
            story.append(Paragraph(
                "✅ <b>Positive:</b> Contract appears to have reasonable terms",
                self.styles['Success']
            ))
        
        return story

    def _create_contract_overview(self, analysis_data: Dict[str, Any], filename: str) -> List:
        """Create contract overview section"""
        story = []
        
        story.append(Paragraph("Contract Overview", self.styles['SectionHeader']))
        story.append(Spacer(1, 15))
        
        # Contract details
        overview_text = f"""
        <b>Document:</b> {filename}<br/>
        <b>Analysis Date:</b> {datetime.now().strftime("%B %d, %Y")}<br/>
        <b>Risk Profile:</b> {analysis_data.get('risk_level', 'UNKNOWN')} ({analysis_data.get('risk_score', 0)}/30)<br/>
        <b>Analysis Scope:</b> Legal risk assessment, compliance review, and negotiation strategy
        """
        
        story.append(Paragraph(overview_text, self.styles['Summary']))
        story.append(Spacer(1, 15))
        
        # Risk distribution
        story.append(Paragraph("Risk Distribution", self.styles['SubsectionHeader']))
        
        risks = analysis_data.get('risks', [])
        risk_categories = {}
        for risk in risks:
            category = risk.get('category', 'Other')
            if category not in risk_categories:
                risk_categories[category] = {'high': 0, 'medium': 0, 'low': 0}
            severity = risk.get('severity', 'low')
            risk_categories[category][severity] += 1
        
        if risk_categories:
            cat_data = [["Category", "High", "Medium", "Low", "Total"]]
            for category, counts in risk_categories.items():
                total = sum(counts.values())
                cat_data.append([
                    category,
                    str(counts['high']),
                    str(counts['medium']),
                    str(counts['low']),
                    str(total)
                ])
            
            cat_table = Table(cat_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            cat_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(cat_table)
        
        return story

    def _create_detailed_risk_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """Create detailed risk analysis with explanations and negotiation points"""
        story = []
        
        story.append(Paragraph("Detailed Risk Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 15))
        
        risks = analysis_data.get('risks', [])
        
        if not risks:
            story.append(Paragraph("✅ No significant risks detected in this contract.", self.styles['Success']))
            return story
        
        # Group risks by category
        risk_categories = {}
        for risk in risks:
            category = risk.get('category', 'Other')
            if category not in risk_categories:
                risk_categories[category] = []
            risk_categories[category].append(risk)
        
        for category, category_risks in risk_categories.items():
            # Category header
            story.append(Paragraph(f"{category} Analysis", self.styles['SubsectionHeader']))
            
            # Category explanation
            if category in self.negotiation_guidance:
                explanation = self.negotiation_guidance[category]['explanation']
                story.append(Paragraph(f"<b>What this means:</b> {explanation}", self.styles['Summary']))
                story.append(Spacer(1, 10))
            
            # Individual risks
            for i, risk in enumerate(category_risks, 1):
                severity = risk.get('severity', 'low')
                severity_color = self._get_severity_color(severity)
                
                risk_text = f"""
                <b>{i}. {risk.get('category', 'Risk')} ({severity.upper()})</b><br/>
                <b>Issue:</b> {risk.get('description', 'No description')}<br/>
                <b>Location:</b> {risk.get('clause', 'Not specified')}<br/>
                <b>Current Recommendation:</b> {risk.get('recommendation', 'Review required')}
                """
                
                story.append(Paragraph(risk_text, self.styles['RiskItem']))
                
                # Add negotiation points if available
                if category in self.negotiation_guidance:
                    guidance = self.negotiation_guidance[category]
                    
                    # Check for red flags
                    red_flags = []
                    for flag in guidance['red_flags']:
                        if flag.lower() in risk.get('clause', '').lower():
                            red_flags.append(flag)
                    
                    if red_flags:
                        red_flag_text = "<b>⚠️ Red Flags Detected:</b><br/>"
                        for flag in red_flags:
                            red_flag_text += f"• {flag}<br/>"
                        story.append(Paragraph(red_flag_text, self.styles['Warning']))
                    
                    # Add negotiation points
                    negotiation_text = "<b>💡 Negotiation Points:</b><br/>"
                    for point in guidance['negotiation_points'][:3]:  # Show top 3
                        negotiation_text += f"• {point}<br/>"
                    story.append(Paragraph(negotiation_text, self.styles['NegotiationPoint']))
                    
                    # Market standard
                    market_text = f"<b>📊 Market Standard:</b> {guidance['market_standard']}"
                    story.append(Paragraph(market_text, self.styles['Summary']))
                
                story.append(Spacer(1, 15))
        
        return story

    def _create_compliance_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """Create compliance analysis section"""
        story = []
        
        story.append(Paragraph("Compliance Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 15))
        
        compliance = analysis_data.get('compliance', [])
        
        if not compliance:
            story.append(Paragraph("✅ No specific compliance issues identified.", self.styles['Success']))
            return story
        
        # Group by regulation
        compliance_by_reg = {}
        for comp in compliance:
            regulation = comp.get('regulation', 'Other')
            if regulation not in compliance_by_reg:
                compliance_by_reg[regulation] = []
            compliance_by_reg[regulation].append(comp)
        
        for regulation, reg_compliance in compliance_by_reg.items():
            story.append(Paragraph(f"{regulation} Compliance", self.styles['SubsectionHeader']))
            
            for i, comp in enumerate(reg_compliance, 1):
                status = comp.get('status', 'check')
                status_icon = "⚠️" if status == "warning" else "❌" if status == "critical" else "✅"
                
                comp_text = f"""
                <b>{i}. {status_icon} {comp.get('description', 'Compliance issue')}</b><br/>
                <b>Status:</b> {status.upper()}<br/>
                <b>Location:</b> {comp.get('clause', 'Not specified')}<br/>
                <b>Action:</b> {comp.get('recommendation', 'Review with legal counsel')}
                """
                
                story.append(Paragraph(comp_text, self.styles['RiskItem']))
                story.append(Spacer(1, 10))
        
        return story

    def _create_negotiation_strategy(self, analysis_data: Dict[str, Any]) -> List:
        """Create negotiation strategy section"""
        story = []
        
        story.append(Paragraph("Negotiation Strategy", self.styles['SectionHeader']))
        story.append(Spacer(1, 15))
        
        risks = analysis_data.get('risks', [])
        risk_level = analysis_data.get('risk_level', 'UNKNOWN')
        
        # Overall strategy
        if risk_level in ['CRITICAL', 'HIGH']:
            strategy_text = """
            <b>🚨 High-Risk Contract - Aggressive Negotiation Required</b><br/>
            This contract contains significant risks that require immediate attention. 
            Consider requesting substantial modifications or walking away if terms cannot be improved.
            """
        elif risk_level == 'MEDIUM':
            strategy_text = """
            <b>⚖️ Medium-Risk Contract - Balanced Negotiation Approach</b><br/>
            This contract has some concerning terms but is generally negotiable. 
            Focus on the highest-risk items while accepting reasonable terms on others.
            """
        else:
            strategy_text = """
            <b>✅ Low-Risk Contract - Standard Negotiation</b><br/>
            This contract appears to have reasonable terms. Focus on minor improvements 
            and ensuring all terms are clearly understood.
            """
        
        story.append(Paragraph(strategy_text, self.styles['Summary']))
        story.append(Spacer(1, 15))
        
        # Priority negotiation items
        high_risks = [r for r in risks if r.get('severity') == 'high']
        medium_risks = [r for r in risks if r.get('severity') == 'medium']
        
        if high_risks:
            story.append(Paragraph("🔥 High Priority Negotiation Items", self.styles['SubsectionHeader']))
            for i, risk in enumerate(high_risks, 1):
                story.append(Paragraph(
                    f"{i}. <b>{risk.get('category', 'Risk')}:</b> {risk.get('recommendation', 'Review required')}",
                    self.styles['Warning']
                ))
            story.append(Spacer(1, 10))
        
        if medium_risks:
            story.append(Paragraph("⚖️ Medium Priority Negotiation Items", self.styles['SubsectionHeader']))
            for i, risk in enumerate(medium_risks, 1):
                story.append(Paragraph(
                    f"{i}. <b>{risk.get('category', 'Risk')}:</b> {risk.get('recommendation', 'Review required')}",
                    self.styles['Summary']
                ))
        
        return story

    def _create_recommendations(self, analysis_data: Dict[str, Any]) -> List:
        """Create comprehensive recommendations section"""
        story = []
        
        story.append(Paragraph("Strategic Recommendations", self.styles['SectionHeader']))
        story.append(Spacer(1, 15))
        
        risk_level = analysis_data.get('risk_level', 'UNKNOWN')
        risk_score = analysis_data.get('risk_score', 0)
        
        # Overall recommendation
        if risk_level in ['CRITICAL', 'HIGH']:
            overall_rec = """
            <b>🚨 IMMEDIATE ACTION REQUIRED</b><br/>
            This contract presents significant legal and financial risks. 
            We strongly recommend extensive negotiations or reconsideration of the agreement.
            """
        elif risk_level == 'MEDIUM':
            overall_rec = """
            <b>⚖️ NEGOTIATION RECOMMENDED</b><br/>
            This contract has some concerning terms that should be addressed 
            before signing. Focus on the highest-risk items.
            """
        else:
            overall_rec = """
            <b>✅ GENERALLY ACCEPTABLE</b><br/>
            This contract appears to have reasonable terms. 
            Minor negotiations may be beneficial but are not critical.
            """
        
        story.append(Paragraph(overall_rec, self.styles['Summary']))
        story.append(Spacer(1, 15))
        
        # Specific recommendations
        story.append(Paragraph("Specific Actions", self.styles['SubsectionHeader']))
        
        recommendations = [
            "Review all high-risk items with legal counsel",
            "Negotiate liability caps and indemnification terms",
            "Ensure payment terms are reasonable and achievable",
            "Verify compliance with applicable regulations",
            "Request clarification on ambiguous terms",
            "Consider insurance requirements for high-risk contracts",
            "Document all negotiations and changes"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['RiskItem']))
        
        story.append(Spacer(1, 15))
        
        # Next steps
        story.append(Paragraph("Next Steps", self.styles['SubsectionHeader']))
        
        if risk_level in ['CRITICAL', 'HIGH']:
            next_steps = [
                "Schedule immediate legal review",
                "Prepare negotiation strategy",
                "Identify deal-breaker terms",
                "Consider alternative suppliers/vendors"
            ]
        elif risk_level == 'MEDIUM':
            next_steps = [
                "Prioritize high-risk items for negotiation",
                "Prepare counter-proposals",
                "Set negotiation timeline",
                "Identify acceptable compromises"
            ]
        else:
            next_steps = [
                "Review terms with stakeholders",
                "Prepare minor negotiation requests",
                "Set signing timeline",
                "Plan implementation"
            ]
        
        for i, step in enumerate(next_steps, 1):
            story.append(Paragraph(f"{i}. {step}", self.styles['RiskItem']))
        
        return story

    def _create_technical_details(self, analysis_data: Dict[str, Any]) -> List:
        """Create technical details section"""
        story = []
        
        story.append(Paragraph("Technical Details", self.styles['SectionHeader']))
        story.append(Spacer(1, 15))
        
        # Analysis metadata
        tech_data = [
            ["Analysis ID", analysis_data.get('analysis_id', 'N/A')],
            ["Analysis Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Risk Algorithm Version", "2.0 (Enhanced)"],
            ["AI Model Used", "Hugging Face GPT-2 + Pattern Matching"],
            ["Confidence Level", "High"],
            ["Analysis Scope", "Legal Risk + Compliance + Negotiation Strategy"]
        ]
        
        tech_table = Table(tech_data, colWidths=[2.5*inch, 4*inch])
        tech_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(tech_table)
        story.append(Spacer(1, 20))
        
        # Disclaimer
        disclaimer = """
        <b>Disclaimer:</b> This analysis is provided for informational purposes only and does not constitute legal advice. 
        Always consult with qualified legal counsel before making decisions based on this analysis. 
        The analysis is based on automated review and may not capture all nuances of complex legal documents.
        """
        
        story.append(Paragraph(disclaimer, self.styles['Summary']))
        
        return story

    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level"""
        colors_map = {
            'CRITICAL': 'red',
            'HIGH': 'orange',
            'MEDIUM': 'yellow',
            'LOW': 'green',
            'MINIMAL': 'blue'
        }
        return colors_map.get(risk_level.upper(), 'black')

    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors_map = {
            'high': 'red',
            'medium': 'orange',
            'low': 'green'
        }
        return colors_map.get(severity.lower(), 'black')

    def _get_risk_description(self, risk_level: str) -> str:
        """Get description for risk level"""
        descriptions = {
            'CRITICAL': 'Immediate legal review required. Significant risks present.',
            'HIGH': 'Extensive negotiations recommended. Multiple concerning terms.',
            'MEDIUM': 'Some negotiation needed. Standard contract with risks.',
            'LOW': 'Generally acceptable terms. Minor improvements possible.',
            'MINIMAL': 'Very low risk. Standard contract terms.'
        }
        return descriptions.get(risk_level.upper(), 'Risk level unclear.') 