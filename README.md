# Nuraxi Foundry Demo Prototype

**King Faisal Specialist Hospital & Research Centre (KFSHRC)**
*Version 1.0 | January 2026*

## Overview

This prototype demonstrates the Nuraxi Foundry platform's capabilities for transforming fragmented clinical data from multiple hospital systems into a unified, de-identified, research-ready format.

## Demo Objectives

1. **Cross-system Patient Linkage**: Tokenization enables building longitudinal patient records across multiple disconnected hospital systems while maintaining 100% anonymity.

2. **Data Transformation**: Conversion of fragmented, unstructured clinical data into standardized OMOP Common Data Model format.

3. **De-identification**: Safe Harbor compliant de-identification with realistic surrogate data (HiPS methodology).

4. **Research Capabilities**: Cohort queries and analytics on the transformed data.

5. **AI Clinical Intelligence**: Clinical agents reviewing patient encounters and generating actionable insights.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Nuraxi Foundry Demo                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   HIS        │    │    LAB       │    │    EMR       │      │
│  │   System     │    │   System     │    │   System     │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                   │
│                             ▼                                   │
│                    ┌────────────────┐                          │
│                    │  Tokenization  │                          │
│                    │    Service     │                          │
│                    └────────┬───────┘                          │
│                             │                                   │
│                             ▼                                   │
│                    ┌────────────────┐                          │
│                    │De-identification│                          │
│                    │ (Safe Harbor)  │                          │
│                    └────────┬───────┘                          │
│                             │                                   │
│                             ▼                                   │
│                    ┌────────────────┐                          │
│                    │     OMOP       │                          │
│                    │  Transformer   │                          │
│                    └────────┬───────┘                          │
│                             │                                   │
│              ┌──────────────┼──────────────┐                   │
│              ▼              ▼              ▼                   │
│      ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│      │  Cohort    │  │  Analytics │  │ Clinical   │           │
│      │  Queries   │  │  Dashboard │  │ AI Agent   │           │
│      └────────────┘  └────────────┘  └────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.12+ with FastAPI
- **Frontend**: React 18 with TypeScript
- **Data Model**: OMOP CDM v5.4
- **Vocabularies**: SNOMED, LOINC, RxNorm

## Quick Start

### Prerequisites

- Python 3.12
- Node.js 22+

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Access the Demo

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **API ReDoc**: http://localhost:8000/api/redoc

## API Endpoints

### Full Pipeline
```bash
# Run complete demo pipeline
POST /api/demo/full-pipeline?num_patients=30
```

### Individual Steps
```bash
# Generate synthetic data
POST /api/demo/generate-data

# Tokenize for patient linkage
POST /api/demo/tokenize

# De-identify data
POST /api/demo/deidentify

# Transform to OMOP
POST /api/demo/transform-to-omop

# Query cohorts
POST /api/demo/cohort/query
{"query_name": "diabetic_patients"}

# AI patient analysis
GET /api/demo/ai/analyze-patient/{person_id}
```

## Key Features Demonstrated

### 1. Synthetic Saudi Patient Data

Generates realistic patient data including:
- Saudi names and family names
- National ID numbers
- Regional addresses (all Saudi regions)
- Common diagnoses seen at KFSHRC
- Lab results with LOINC codes
- Medications with RxNorm codes

### 2. Cross-System Patient Linkage

- Cryptographic tokenization using HMAC-SHA256
- Links patients across HIS, LAB, EMR, PHARMACY, RAD, ICU systems
- Maintains referential integrity
- 100% anonymous - tokens cannot be reversed

### 3. De-identification (Safe Harbor + HiPS)

- Removes all 18 HIPAA Safe Harbor identifiers
- Date shifting with patient-consistent offsets
- Surrogate name generation
- Clinical notes redaction
- Preserves research utility

### 4. OMOP CDM Transformation

- Maps to OMOP CDM v5.4 tables:
  - PERSON
  - VISIT_OCCURRENCE
  - CONDITION_OCCURRENCE
  - MEASUREMENT
  - DRUG_EXPOSURE
- Vocabulary mappings:
  - ICD-10 → SNOMED
  - Local labs → LOINC
  - Medications → RxNorm

### 5. Research Cohort Queries

Pre-defined cohorts:
- Diabetic patients
- CKD patients on dialysis
- Transplant recipients
- Oncology patients
- Elderly cardiac patients

### 6. AI Clinical Intelligence

- Critical lab value detection
- Drug interaction screening
- Quality metric analysis
- Visit pattern insights
- Risk scoring

## Project Structure

```
foundry/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── patient.py
│   │   │   └── omop.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── synthetic_data.py
│   │   │   ├── tokenization.py
│   │   │   ├── deidentification.py
│   │   │   ├── omop_transformer.py
│   │   │   ├── cohort_query.py
│   │   │   └── clinical_ai.py
│   │   ├── __init__.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── README.md
```

## Next Steps for Production

1. **Data Persistence**: Add PostgreSQL database for OMOP CDM storage
2. **Authentication**: Implement OAuth2/OIDC for API security
3. **Audit Logging**: Add comprehensive audit trails
4. **Scaling**: Deploy with Kubernetes for high availability
5. **ML Models**: Integrate production clinical ML models
6. **Vocabulary Updates**: Connect to OHDSI Athena for vocabulary updates

## Contact

For questions about this demo, contact the Nuraxi Foundry team.

---

*This is a demonstration prototype using 100% synthetic data. No real patient data is used.*
