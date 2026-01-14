"""
API Routes for the Nuraxi Foundry Demo

Provides REST endpoints for demonstrating all platform capabilities.
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from typing import Optional, List
from pydantic import BaseModel

from ..services import (
    SyntheticDataGenerator,
    TokenizationService,
    DeidentificationService,
    OMOPTransformer,
    CohortQueryService,
    ClinicalAIAgent,
)
from ..services.csv_parser import CSVParserService, generate_deidentified_csv

router = APIRouter()

# Initialize services (in production, these would be dependency injected)
data_generator = SyntheticDataGenerator(seed=42)
tokenization_service = TokenizationService()
deid_service = DeidentificationService()
omop_transformer = OMOPTransformer()
cohort_service = CohortQueryService()
clinical_ai = ClinicalAIAgent()
csv_parser = CSVParserService()

# Cache for demo data
_demo_data_cache = {}


class DemoDataRequest(BaseModel):
    """Request for generating demo data."""
    num_single_system_patients: int = 20
    num_multi_system_patients: int = 10
    seed: Optional[int] = 42


class CohortQueryRequest(BaseModel):
    """Request for custom cohort query."""
    query_name: str


# ============ Data Generation Endpoints ============

@router.post("/demo/generate-data")
async def generate_demo_data(request: DemoDataRequest):
    """
    Generate synthetic Saudi patient data for the demo.
    This creates realistic patient records across multiple hospital systems.
    """
    global _demo_data_cache

    generator = SyntheticDataGenerator(seed=request.seed or 42)
    raw_data = generator.generate_demo_dataset(
        num_single_system_patients=request.num_single_system_patients,
        num_multi_system_patients=request.num_multi_system_patients,
    )

    _demo_data_cache["raw_data"] = raw_data

    return {
        "status": "success",
        "message": "Synthetic patient data generated",
        "summary": raw_data["summary"],
        "sample_patient": raw_data["patients"][0].model_dump() if raw_data["patients"] else None,
    }


@router.get("/demo/raw-data/summary")
async def get_raw_data_summary():
    """Get summary of the generated raw data."""
    if "raw_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="No data generated yet. Call /demo/generate-data first.")

    return _demo_data_cache["raw_data"]["summary"]


# ============ Tokenization Endpoints ============

@router.post("/demo/tokenize")
async def tokenize_patients():
    """
    Demonstrate cross-system patient linkage using tokenization.
    Links fragmented records from multiple hospital systems.
    """
    if "raw_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="No data generated yet. Call /demo/generate-data first.")

    patients = _demo_data_cache["raw_data"]["patients"]

    # Perform tokenization
    result = tokenization_service.demonstrate_linkage(patients)

    # Store tokens for later use
    _demo_data_cache["patient_tokens"] = tokenization_service.tokenize_patient_batch(patients)
    _demo_data_cache["linked_patients"] = result["linked_record_details"]

    return {
        "status": "success",
        "message": "Patient records tokenized and linked",
        "results": result,
    }


@router.get("/demo/linkage-demo")
async def demonstrate_linkage():
    """
    Show a detailed demonstration of how patient linkage works.
    """
    if "raw_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="No data generated yet")

    # Generate a multi-system patient specifically for demo
    generator = SyntheticDataGenerator(seed=99)
    patients, encounters, observations = generator.generate_multi_system_patient()

    # Tokenize to show linkage
    demo_tokens = {}
    for patient in patients:
        token = tokenization_service.generate_token(patient)
        demo_tokens[patient.source_patient_id] = {
            "token": token,
            "source_system": patient.source_system.value,
            "mrn": patient.mrn,
            "name": f"{patient.first_name} {patient.last_name}",
        }

    # All should have the same token (same person)
    unique_tokens = set(v["token"] for v in demo_tokens.values())

    return {
        "scenario": "Same patient appearing in 4 different hospital systems",
        "patient_records": list(demo_tokens.values()),
        "linkage_result": {
            "records_found": len(patients),
            "unique_tokens_generated": len(unique_tokens),
            "successfully_linked": len(unique_tokens) == 1,
            "common_token": list(unique_tokens)[0] if unique_tokens else None,
        },
        "explanation": "All records share the same National ID and DOB, so they receive the same anonymous token, enabling cross-system linkage without exposing patient identity.",
    }


# ============ De-identification Endpoints ============

@router.post("/demo/deidentify")
async def deidentify_data():
    """
    Demonstrate Safe Harbor + HiPS de-identification.
    Transforms PHI into research-ready anonymous data.
    """
    if "raw_data" not in _demo_data_cache or "patient_tokens" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="Data not ready. Run /demo/generate-data and /demo/tokenize first.")

    raw_data = _demo_data_cache["raw_data"]
    tokens = _demo_data_cache["patient_tokens"]

    # De-identify the dataset
    deidentified = deid_service.deidentify_dataset(
        patients=raw_data["patients"],
        encounters=raw_data["encounters"],
        observations=raw_data["observations"],
        patient_tokens=tokens,
    )

    _demo_data_cache["deidentified_data"] = deidentified

    report = deid_service.get_deidentification_report()

    return {
        "status": "success",
        "message": "Data de-identified using Safe Harbor + HiPS methodology",
        "report": report,
        "sample_deidentified_patient": deidentified["patients"][0] if deidentified["patients"] else None,
    }


@router.get("/demo/deidentification-demo")
async def demonstrate_deidentification():
    """
    Show before/after comparison of de-identification.
    """
    if "raw_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="No data generated yet")

    # Get a sample patient
    patient = _demo_data_cache["raw_data"]["patients"][0]
    token = tokenization_service.generate_token(patient)

    # Show transformation
    demo = deid_service.demonstrate_deidentification(patient, token)

    return {
        "title": "De-identification Demonstration",
        "description": "Shows how PHI is transformed while preserving research utility",
        "before_after": demo,
        "safe_harbor_compliance": {
            "method": "Safe Harbor + HiPS Hybrid",
            "identifiers_removed": 18,
            "data_utility_preserved": True,
        },
    }


# ============ OMOP Transformation Endpoints ============

@router.post("/demo/transform-to-omop")
async def transform_to_omop():
    """
    Transform de-identified data into OMOP Common Data Model format.
    """
    if "deidentified_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="Data not de-identified yet. Run /demo/deidentify first.")

    deidentified = _demo_data_cache["deidentified_data"]

    # Transform to OMOP
    omop_data = omop_transformer.transform_dataset(deidentified)

    _demo_data_cache["omop_data"] = omop_data

    # Load into cohort service
    cohort_service.load_omop_data(omop_data)

    report = omop_transformer.get_transformation_report()

    return {
        "status": "success",
        "message": "Data transformed to OMOP CDM v5.4 format",
        "report": report,
        "omop_tables_created": list(omop_data.keys()),
        "sample_person": omop_data["person"][0] if omop_data["person"] else None,
    }


@router.get("/demo/omop-transformation-demo")
async def demonstrate_omop_transformation():
    """
    Show how source data is mapped to OMOP CDM.
    """
    if "deidentified_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="Data not ready")

    deidentified = _demo_data_cache["deidentified_data"]

    demos = []

    # Demo patient transformation
    if deidentified["patients"]:
        patient_demo = omop_transformer.demonstrate_transformation(
            deidentified["patients"][0], "patient"
        )
        demos.append(patient_demo)

    # Demo encounter transformation
    if deidentified["encounters"]:
        encounter_demo = omop_transformer.demonstrate_transformation(
            deidentified["encounters"][0], "encounter"
        )
        demos.append(encounter_demo)

    # Demo lab transformation
    lab_obs = next(
        (o for o in deidentified["observations"] if o.get("observation_type") == "lab_result"),
        None
    )
    if lab_obs:
        lab_demo = omop_transformer.demonstrate_transformation(lab_obs, "lab_result")
        demos.append(lab_demo)

    return {
        "title": "OMOP CDM Transformation Demonstration",
        "description": "Shows how heterogeneous source data is standardized to OMOP format",
        "transformations": demos,
        "omop_version": "5.4",
        "vocabularies": ["SNOMED", "LOINC", "RxNorm"],
    }


# ============ Cohort Query Endpoints ============

@router.get("/demo/cohort/available-queries")
async def get_available_queries():
    """Get list of available predefined cohort queries."""
    return {
        "queries": cohort_service.get_available_queries(),
    }


@router.post("/demo/cohort/query")
async def run_cohort_query(request: CohortQueryRequest):
    """Run a predefined cohort query."""
    if "omop_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="OMOP data not ready. Run /demo/transform-to-omop first.")

    result = cohort_service.run_predefined_query(request.query_name)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "status": "success",
        "cohort_result": result,
    }


@router.get("/demo/cohort/analytics")
async def get_analytics():
    """Get analytics summary of the OMOP data."""
    if "omop_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="OMOP data not ready")

    return cohort_service.get_analytics_summary()


# ============ Clinical AI Endpoints ============

@router.get("/demo/ai/analyze-patient/{person_id}")
async def analyze_patient(person_id: int):
    """
    Run AI analysis on a specific patient.
    """
    if "omop_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="OMOP data not ready")

    omop_data = _demo_data_cache["omop_data"]

    # Find person
    persons = omop_data.get("person", [])
    person = next((p for p in persons if p["person_id"] == person_id), None)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

    # Get related data
    visits = [v for v in omop_data.get("visit_occurrence", []) if v["person_id"] == person_id]
    conditions = [c for c in omop_data.get("condition_occurrence", []) if c["person_id"] == person_id]
    measurements = [m for m in omop_data.get("measurement", []) if m["person_id"] == person_id]
    drugs = [d for d in omop_data.get("drug_exposure", []) if d["person_id"] == person_id]

    # Run analysis
    result = clinical_ai.analyze_patient_data(
        patient_token=person.get("person_source_value", str(person_id)),
        person_data=person,
        visits=visits,
        conditions=conditions,
        measurements=measurements,
        drugs=drugs,
    )

    return {
        "status": "success",
        "analysis": result,
    }


@router.post("/demo/ai/analyze-cohort")
async def analyze_cohort(request: CohortQueryRequest):
    """
    Run AI analysis on a cohort of patients.
    """
    if "omop_data" not in _demo_data_cache:
        raise HTTPException(status_code=404, detail="OMOP data not ready")

    # First build the cohort
    cohort_result = cohort_service.run_predefined_query(request.query_name)
    if "error" in cohort_result:
        raise HTTPException(status_code=400, detail=cohort_result["error"])

    member_ids = cohort_result.get("member_ids", [])

    if not member_ids:
        return {
            "status": "success",
            "message": "No patients in cohort",
            "cohort_analysis": None,
        }

    # Analyze cohort
    analysis = clinical_ai.analyze_cohort(member_ids, _demo_data_cache["omop_data"])

    return {
        "status": "success",
        "cohort_info": {
            "name": cohort_result.get("cohort_name"),
            "size": len(member_ids),
        },
        "cohort_analysis": analysis,
    }


# ============ Full Pipeline Demo Endpoint ============

@router.post("/demo/full-pipeline")
async def run_full_pipeline(
    num_patients: int = Query(default=30, ge=5, le=100),
    seed: int = Query(default=42),
):
    """
    Run the complete demo pipeline:
    1. Generate synthetic Saudi patient data
    2. Tokenize for cross-system linkage
    3. De-identify using Safe Harbor + HiPS
    4. Transform to OMOP CDM
    5. Generate analytics and AI insights
    """
    global _demo_data_cache

    results = {
        "pipeline_steps": [],
        "overall_status": "in_progress",
    }

    try:
        # Step 1: Generate data
        generator = SyntheticDataGenerator(seed=seed)
        raw_data = generator.generate_demo_dataset(
            num_single_system_patients=int(num_patients * 0.7),
            num_multi_system_patients=int(num_patients * 0.3),
        )
        _demo_data_cache["raw_data"] = raw_data
        results["pipeline_steps"].append({
            "step": 1,
            "name": "Data Generation",
            "status": "completed",
            "result": raw_data["summary"],
        })

        # Step 2: Tokenization
        tokens = tokenization_service.tokenize_patient_batch(raw_data["patients"])
        _demo_data_cache["patient_tokens"] = tokens
        linkage_result = tokenization_service.demonstrate_linkage(raw_data["patients"])
        results["pipeline_steps"].append({
            "step": 2,
            "name": "Patient Linkage (Tokenization)",
            "status": "completed",
            "result": linkage_result["statistics"],
        })

        # Step 3: De-identification
        deidentified = deid_service.deidentify_dataset(
            patients=raw_data["patients"],
            encounters=raw_data["encounters"],
            observations=raw_data["observations"],
            patient_tokens=tokens,
        )
        _demo_data_cache["deidentified_data"] = deidentified
        deid_report = deid_service.get_deidentification_report()
        results["pipeline_steps"].append({
            "step": 3,
            "name": "De-identification (Safe Harbor + HiPS)",
            "status": "completed",
            "result": {
                "patients_deidentified": deid_report["total_patients_deidentified"],
                "method": deid_report["safe_harbor_compliance"]["method"],
            },
        })

        # Step 4: OMOP Transformation
        omop_data = omop_transformer.transform_dataset(deidentified)
        _demo_data_cache["omop_data"] = omop_data
        cohort_service.load_omop_data(omop_data)
        omop_report = omop_transformer.get_transformation_report()
        results["pipeline_steps"].append({
            "step": 4,
            "name": "OMOP CDM Transformation",
            "status": "completed",
            "result": {
                "persons": omop_report["unique_persons_created"],
                "visits": omop_report["visits_created"],
                "conditions": omop_report["conditions_created"],
                "measurements": omop_report["measurements_created"],
                "drugs": omop_report["drug_exposures_created"],
            },
        })

        # Step 5: Analytics
        analytics = cohort_service.get_analytics_summary()
        results["pipeline_steps"].append({
            "step": 5,
            "name": "Analytics & Research Capabilities",
            "status": "completed",
            "result": analytics["data_summary"],
        })

        results["overall_status"] = "completed"
        results["message"] = "Full pipeline executed successfully"

    except Exception as e:
        results["overall_status"] = "failed"
        results["error"] = str(e)

    return results


# ============ Demo Status Endpoint ============

@router.get("/demo/status")
async def get_demo_status():
    """Get the current status of the demo data pipeline."""
    return {
        "data_generated": "raw_data" in _demo_data_cache,
        "tokenized": "patient_tokens" in _demo_data_cache,
        "deidentified": "deidentified_data" in _demo_data_cache,
        "omop_transformed": "omop_data" in _demo_data_cache,
        "ready_for_queries": "omop_data" in _demo_data_cache,
        "cached_data_keys": list(_demo_data_cache.keys()),
    }


@router.delete("/demo/reset")
async def reset_demo():
    """Reset all demo data and start fresh."""
    global _demo_data_cache
    _demo_data_cache = {}
    return {"status": "success", "message": "Demo data cleared"}


# ============ CSV Upload/Download Endpoints ============

@router.post("/demo/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file containing patient data for de-identification.

    The CSV must contain at minimum: first_name, last_name, date_of_birth, gender

    Optional columns: national_id, mrn, middle_name, family_name, phone_number,
    email, address_line1, city, region, postal_code, encounter_id, encounter_type,
    admission_date, discharge_date, department, diagnosis_code, diagnosis_description,
    chief_complaint, clinical_notes

    Returns the processed and de-identified data.
    """
    global _demo_data_cache

    # Validate file type
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    # Read file content
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    # Parse CSV
    parse_result = csv_parser.parse_csv(csv_content)

    if not parse_result.success and parse_result.valid_row_count == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "CSV parsing failed",
                "errors": parse_result.errors,
            }
        )

    # Store parsed data
    _demo_data_cache["raw_data"] = {
        "patients": parse_result.patients,
        "encounters": parse_result.encounters,
        "observations": [],  # CSV doesn't include observations
        "summary": {
            "total_patient_records": len(parse_result.patients),
            "unique_individuals": len(parse_result.patients),
            "total_encounters": len(parse_result.encounters),
            "total_observations": 0,
            "source": "csv_upload",
            "filename": file.filename,
        },
    }
    _demo_data_cache["csv_upload"] = True

    # Run tokenization
    tokens = tokenization_service.tokenize_patient_batch(parse_result.patients)
    _demo_data_cache["patient_tokens"] = tokens

    # Run de-identification
    deid_service_instance = DeidentificationService()  # Fresh instance for new upload
    deidentified = deid_service_instance.deidentify_dataset(
        patients=parse_result.patients,
        encounters=parse_result.encounters,
        observations=[],
        patient_tokens=tokens,
    )
    _demo_data_cache["deidentified_data"] = deidentified
    deid_report = deid_service_instance.get_deidentification_report()

    # Transform to OMOP
    omop_data = omop_transformer.transform_dataset(deidentified)
    _demo_data_cache["omop_data"] = omop_data
    cohort_service.load_omop_data(omop_data)

    return {
        "status": "success",
        "message": f"CSV processed successfully: {parse_result.valid_row_count} records de-identified",
        "parsing": {
            "total_rows": parse_result.row_count,
            "valid_rows": parse_result.valid_row_count,
            "errors": parse_result.errors[:5] if parse_result.errors else [],  # Limit errors shown
            "warnings": parse_result.warnings[:5] if parse_result.warnings else [],
        },
        "deidentification": {
            "patients_processed": deid_report["total_patients_deidentified"],
            "method": "PDPL-Compliant + HiPS",
        },
        "download_available": True,
    }


@router.get("/demo/download-csv")
async def download_deidentified_csv():
    """
    Download the de-identified data as a CSV file.

    Must have previously uploaded and processed a CSV via /demo/upload-csv
    or run the full pipeline via /demo/full-pipeline.
    """
    if "deidentified_data" not in _demo_data_cache:
        raise HTTPException(
            status_code=404,
            detail="No de-identified data available. Upload a CSV or run the pipeline first."
        )

    deidentified = _demo_data_cache["deidentified_data"]

    # Generate CSV content
    csv_content = generate_deidentified_csv(
        deidentified_patients=deidentified["patients"],
        deidentified_encounters=deidentified["encounters"],
    )

    # Determine filename
    if _demo_data_cache.get("csv_upload"):
        original_name = _demo_data_cache.get("raw_data", {}).get("summary", {}).get("filename", "data")
        filename = f"deidentified_{original_name}"
    else:
        filename = "deidentified_patient_data.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
