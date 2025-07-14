# AI Contract Risk Analyzer - FastAPI Service

This is the AI microservice for the Contract Risk Analyzer application. It provides intelligent contract analysis using pattern recognition and risk assessment algorithms.

## Features

- **Risk Analysis**: Detects payment terms, liability limitations, termination clauses, confidentiality, and IP risks
- **Compliance Checking**: Identifies GDPR, SOX, and HIPAA compliance requirements
- **Risk Scoring**: Provides numerical risk scores and severity levels
- **Detailed Reports**: Generates comprehensive analysis with recommendations

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Service
```bash
python main.py
```

The service will start on `http://localhost:8000`

### 3. API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### Health Check
- `GET /health` - Check service status

### Analysis Endpoints
- `POST /analyze` - Analyze contract content (JSON)
- `POST /analyze-file` - Analyze uploaded file

### Example Usage

```bash
# Analyze contract content
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Contract content here...",
    "filename": "contract.txt"
  }'

# Analyze uploaded file
curl -X POST "http://localhost:8000/analyze-file" \
  -F "file=@contract.txt"
```

## Risk Categories

1. **Payment Terms** - Late payment penalties, interest charges
2. **Liability Limitations** - Damage caps, liability exclusions
3. **Termination Clauses** - Notice periods, termination rights
4. **Confidentiality** - NDA terms, trade secrets
5. **Intellectual Property** - Copyright, patents, trademarks

## Compliance Regulations

1. **GDPR** - Data protection and privacy
2. **SOX** - Financial reporting controls
3. **HIPAA** - Health information privacy

## Integration

This service is designed to work with the Next.js frontend. The frontend will call this service for contract analysis and display the results.

## Development

- **Port**: 8000
- **CORS**: Enabled for all origins (configure for production)
- **Logging**: Basic console logging
- **Error Handling**: Comprehensive error responses 