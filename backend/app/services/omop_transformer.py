"""
OMOP CDM Transformer

Transforms fragmented, heterogeneous clinical data into the standardized
OMOP Common Data Model (CDM) v5.4 format for research-ready analysis.

Key transformations:
1. Standardize vocabulary codes (ICD-10 -> SNOMED, local codes -> LOINC)
2. Map source data to OMOP table structures
3. Apply concept mappings for interoperability
4. Generate standardized clinical concepts
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import hashlib

from ..models.patient import Patient, PatientEncounter, ClinicalObservation, GenderType
from ..models.omop import (
    Person, VisitOccurrence, ConditionOccurrence,
    Measurement, Observation, DrugExposure, ProcedureOccurrence
)


@dataclass
class ConceptMapping:
    """Represents a mapping from source code to OMOP concept."""
    source_code: str
    source_vocabulary: str
    target_concept_id: int
    target_concept_name: str
    target_vocabulary: str


class OMOPTransformer:
    """
    Transforms source clinical data into OMOP CDM format.

    The transformation process:
    1. Map patient demographics to OMOP Person table
    2. Map encounters to Visit Occurrence
    3. Map diagnoses to Condition Occurrence
    4. Map lab results to Measurement
    5. Map medications to Drug Exposure
    """

    # OMOP Standard Concepts for Gender
    GENDER_CONCEPTS = {
        GenderType.MALE: 8507,      # Male
        GenderType.FEMALE: 8532,    # Female
        GenderType.OTHER: 8551,     # Unknown
        GenderType.UNKNOWN: 8551,   # Unknown
    }

    # OMOP Visit Type Concepts
    VISIT_CONCEPTS = {
        "inpatient": 9201,          # Inpatient Visit
        "outpatient": 9202,         # Outpatient Visit
        "emergency": 9203,          # Emergency Room Visit
        "icu": 32037,               # Intensive Care
    }

    # Common ICD-10 to SNOMED mappings (subset for demo)
    ICD_TO_SNOMED = {
        "C91.0": (93143009, "Acute lymphoid leukemia"),
        "C50.9": (254837009, "Malignant neoplasm of breast"),
        "N18.9": (709044004, "Chronic kidney disease"),
        "E11.9": (44054006, "Type 2 diabetes mellitus"),
        "I10": (38341003, "Hypertensive disorder"),
        "I25.10": (53741008, "Coronary arteriosclerosis"),
        "I50.9": (84114007, "Heart failure"),
        "K74.60": (19943007, "Cirrhosis of liver"),
        "N18.6": (46177005, "End-stage renal disease"),
        "D57.1": (417357006, "Sickle cell disease"),
        "D56.1": (40108008, "Thalassemia major"),
        "C22.0": (25370001, "Hepatocellular carcinoma"),
        "C18.9": (363406005, "Malignant neoplasm of colon"),
        "C85.9": (118601006, "Non-Hodgkin lymphoma"),
        "C90.0": (109989006, "Multiple myeloma"),
        "Z94.81": (234519009, "Bone marrow transplant"),
        "Z94.0": (70536003, "Kidney transplant"),
        "Z94.4": (18027006, "Liver transplant"),
        "J18.9": (233604007, "Pneumonia"),
        "A41.9": (91302008, "Sepsis"),
        "N17.9": (14669001, "Acute kidney injury"),
        "I63.9": (230690007, "Stroke"),
        "I21.9": (22298006, "Myocardial infarction"),
        "I26.99": (59282003, "Pulmonary embolism"),
        "I82.40": (128053003, "Deep vein thrombosis"),
    }

    # Common LOINC codes for lab measurements
    LOINC_CONCEPTS = {
        "718-7": (3000963, "Hemoglobin"),
        "6690-2": (3010813, "White blood cell count"),
        "777-3": (3024929, "Platelet count"),
        "2160-0": (3016723, "Creatinine"),
        "3094-0": (3013682, "Blood urea nitrogen"),
        "2345-7": (3004501, "Glucose"),
        "4548-4": (3004410, "Hemoglobin A1c"),
        "2951-2": (3019550, "Sodium"),
        "2823-3": (3023103, "Potassium"),
        "1742-6": (3006923, "ALT"),
        "1920-8": (3013721, "AST"),
        "1975-2": (3024128, "Bilirubin"),
        "1751-7": (3024561, "Albumin"),
        "5902-2": (3034426, "Prothrombin time"),
        "6301-6": (3022217, "INR"),
    }

    # RxNorm to OMOP Drug Concepts (subset)
    RXNORM_CONCEPTS = {
        "860975": (19078461, "Metformin"),
        "314076": (1308216, "Lisinopril"),
        "617311": (1545958, "Atorvastatin"),
        "329528": (1332418, "Amlodipine"),
        "904453": (948078, "Omeprazole"),
        "1191": (1112807, "Aspirin"),
        "847230": (35894915, "Insulin glargine"),
        "4603": (956874, "Furosemide"),
        "11289": (1310149, "Warfarin"),
        "42316": (950637, "Tacrolimus"),
        "68149": (19003999, "Mycophenolate"),
        "227718": (1304850, "Filgrastim"),
        "26225": (1000560, "Ondansetron"),
        "7052": (1110410, "Morphine"),
    }

    def __init__(self):
        self._person_id_counter = 0
        self._visit_id_counter = 0
        self._condition_id_counter = 0
        self._measurement_id_counter = 0
        self._observation_id_counter = 0
        self._drug_id_counter = 0
        self._procedure_id_counter = 0

        # Mapping from patient token to OMOP person_id
        self._token_to_person_id: Dict[str, int] = {}

        # Transformation log
        self._transformation_log: List[Dict] = []

    def _get_person_id(self, patient_token: str) -> int:
        """Get or create a person_id for a patient token."""
        if patient_token not in self._token_to_person_id:
            self._person_id_counter += 1
            self._token_to_person_id[patient_token] = self._person_id_counter
        return self._token_to_person_id[patient_token]

    def _extract_icd_code(self, diagnosis: str) -> Optional[str]:
        """Extract ICD-10 code from a diagnosis string."""
        if not diagnosis:
            return None
        # Look for pattern like (X00.0) at the end
        import re
        match = re.search(r'\(([A-Z]\d{2}\.?\d*)\)', diagnosis)
        if match:
            return match.group(1)
        return None

    def transform_patient_to_person(
        self,
        deidentified_patient: Dict[str, Any],
    ) -> Person:
        """Transform a de-identified patient to OMOP Person."""
        self._transformation_log.append({
            "source_type": "patient",
            "target_type": "person",
            "token": deidentified_patient.get("patient_token"),
        })

        person_id = self._get_person_id(deidentified_patient["patient_token"])

        # Map gender
        gender_value = deidentified_patient.get("gender", "unknown")
        gender_concept_id = self.GENDER_CONCEPTS.get(
            GenderType(gender_value), 8551
        )

        return Person(
            person_id=person_id,
            gender_concept_id=gender_concept_id,
            year_of_birth=deidentified_patient.get("year_of_birth", 1900),
            month_of_birth=deidentified_patient.get("month_of_birth"),
            day_of_birth=None,  # Removed for de-identification
            birth_datetime=None,
            race_concept_id=0,
            ethnicity_concept_id=0,
            person_source_value=deidentified_patient["patient_token"],
            gender_source_value=gender_value,
        )

    def transform_encounter_to_visit(
        self,
        deidentified_encounter: Dict[str, Any],
    ) -> VisitOccurrence:
        """Transform a de-identified encounter to OMOP Visit Occurrence."""
        self._visit_id_counter += 1

        person_id = self._get_person_id(deidentified_encounter["patient_token"])

        # Map visit type
        encounter_type = deidentified_encounter.get("encounter_type", "outpatient")
        visit_concept_id = self.VISIT_CONCEPTS.get(encounter_type, 9202)

        # Parse dates
        admission_date = datetime.fromisoformat(deidentified_encounter["admission_date"])
        discharge_date = None
        if deidentified_encounter.get("discharge_date"):
            discharge_date = datetime.fromisoformat(deidentified_encounter["discharge_date"])

        self._transformation_log.append({
            "source_type": "encounter",
            "target_type": "visit_occurrence",
            "encounter_type": encounter_type,
            "visit_concept_id": visit_concept_id,
        })

        return VisitOccurrence(
            visit_occurrence_id=self._visit_id_counter,
            person_id=person_id,
            visit_concept_id=visit_concept_id,
            visit_start_date=admission_date.date(),
            visit_start_datetime=admission_date,
            visit_end_date=discharge_date.date() if discharge_date else admission_date.date(),
            visit_end_datetime=discharge_date,
            visit_type_concept_id=44818518,  # Visit derived from EHR
            visit_source_value=deidentified_encounter.get("encounter_id"),
        )

    def transform_diagnosis_to_condition(
        self,
        deidentified_encounter: Dict[str, Any],
        visit_occurrence_id: int,
    ) -> Optional[ConditionOccurrence]:
        """Transform a diagnosis to OMOP Condition Occurrence."""
        diagnosis = deidentified_encounter.get("admission_diagnosis")
        if not diagnosis:
            return None

        icd_code = self._extract_icd_code(diagnosis)
        if not icd_code:
            return None

        # Map to SNOMED
        snomed_mapping = self.ICD_TO_SNOMED.get(icd_code)
        if not snomed_mapping:
            concept_id = 0
            concept_name = diagnosis
        else:
            concept_id, concept_name = snomed_mapping

        self._condition_id_counter += 1
        person_id = self._get_person_id(deidentified_encounter["patient_token"])

        admission_date = datetime.fromisoformat(deidentified_encounter["admission_date"])

        self._transformation_log.append({
            "source_type": "diagnosis",
            "target_type": "condition_occurrence",
            "source_code": icd_code,
            "target_concept_id": concept_id,
            "target_concept_name": concept_name,
        })

        return ConditionOccurrence(
            condition_occurrence_id=self._condition_id_counter,
            person_id=person_id,
            condition_concept_id=concept_id,
            condition_start_date=admission_date.date(),
            condition_start_datetime=admission_date,
            condition_type_concept_id=32817,  # EHR problem list entry
            visit_occurrence_id=visit_occurrence_id,
            condition_source_value=icd_code,
        )

    def transform_lab_to_measurement(
        self,
        deidentified_observation: Dict[str, Any],
    ) -> Optional[Measurement]:
        """Transform a lab result to OMOP Measurement."""
        if deidentified_observation.get("observation_type") != "lab_result":
            return None

        loinc_code = deidentified_observation.get("observation_code")
        if not loinc_code:
            return None

        # Map to OMOP concept
        concept_mapping = self.LOINC_CONCEPTS.get(loinc_code)
        if concept_mapping:
            concept_id, concept_name = concept_mapping
        else:
            concept_id = 0
            concept_name = deidentified_observation.get("observation_name", "Unknown")

        self._measurement_id_counter += 1
        person_id = self._get_person_id(deidentified_observation["patient_token"])

        obs_datetime = datetime.fromisoformat(deidentified_observation["observation_datetime"])

        self._transformation_log.append({
            "source_type": "lab_result",
            "target_type": "measurement",
            "source_code": loinc_code,
            "target_concept_id": concept_id,
        })

        return Measurement(
            measurement_id=self._measurement_id_counter,
            person_id=person_id,
            measurement_concept_id=concept_id,
            measurement_date=obs_datetime.date(),
            measurement_datetime=obs_datetime,
            measurement_type_concept_id=44818702,  # Lab result
            value_as_number=deidentified_observation.get("value_numeric"),
            unit_source_value=deidentified_observation.get("value_unit"),
            range_low=deidentified_observation.get("reference_range_low"),
            range_high=deidentified_observation.get("reference_range_high"),
            measurement_source_value=loinc_code,
        )

    def transform_medication_to_drug_exposure(
        self,
        deidentified_observation: Dict[str, Any],
    ) -> Optional[DrugExposure]:
        """Transform a medication to OMOP Drug Exposure."""
        if deidentified_observation.get("observation_type") != "medication":
            return None

        rxnorm_code = deidentified_observation.get("observation_code")
        if not rxnorm_code:
            return None

        # Map to OMOP concept
        concept_mapping = self.RXNORM_CONCEPTS.get(rxnorm_code)
        if concept_mapping:
            concept_id, concept_name = concept_mapping
        else:
            concept_id = 0
            concept_name = deidentified_observation.get("observation_name", "Unknown")

        self._drug_id_counter += 1
        person_id = self._get_person_id(deidentified_observation["patient_token"])

        obs_datetime = datetime.fromisoformat(deidentified_observation["observation_datetime"])

        self._transformation_log.append({
            "source_type": "medication",
            "target_type": "drug_exposure",
            "source_code": rxnorm_code,
            "target_concept_id": concept_id,
        })

        return DrugExposure(
            drug_exposure_id=self._drug_id_counter,
            person_id=person_id,
            drug_concept_id=concept_id,
            drug_exposure_start_date=obs_datetime.date(),
            drug_exposure_start_datetime=obs_datetime,
            drug_exposure_end_date=obs_datetime.date(),  # Single day for demo
            drug_type_concept_id=38000177,  # Prescription written
            sig=deidentified_observation.get("value_text"),
            route_source_value=deidentified_observation.get("route"),
            dose_unit_source_value=deidentified_observation.get("dose"),
            drug_source_value=rxnorm_code,
        )

    def transform_dataset(
        self,
        deidentified_data: Dict[str, List[Dict]],
    ) -> Dict[str, List]:
        """
        Transform an entire de-identified dataset to OMOP CDM format.
        """
        omop_data = {
            "person": [],
            "visit_occurrence": [],
            "condition_occurrence": [],
            "measurement": [],
            "drug_exposure": [],
        }

        # Transform patients to persons.
        # Multi-system patients arrive as several source records that share one
        # anonymous token (same individual). They collapse to a single OMOP
        # person_id, so we emit each person row exactly once to keep the PERSON
        # table at the unique-individual count (single source of truth for N).
        seen_person_ids = set()
        for patient in deidentified_data.get("patients", []):
            person = self.transform_patient_to_person(patient)
            if person.person_id in seen_person_ids:
                continue
            seen_person_ids.add(person.person_id)
            omop_data["person"].append(person.model_dump())

        # Transform encounters to visits and conditions
        for encounter in deidentified_data.get("encounters", []):
            visit = self.transform_encounter_to_visit(encounter)
            omop_data["visit_occurrence"].append(visit.model_dump())

            condition = self.transform_diagnosis_to_condition(
                encounter, visit.visit_occurrence_id
            )
            if condition:
                omop_data["condition_occurrence"].append(condition.model_dump())

        # Transform observations to measurements and drug exposures
        for observation in deidentified_data.get("observations", []):
            if observation.get("observation_type") == "lab_result":
                measurement = self.transform_lab_to_measurement(observation)
                if measurement:
                    omop_data["measurement"].append(measurement.model_dump())
            elif observation.get("observation_type") == "medication":
                drug = self.transform_medication_to_drug_exposure(observation)
                if drug:
                    omop_data["drug_exposure"].append(drug.model_dump())

        return omop_data

    def get_transformation_report(self) -> Dict:
        """Generate a report of transformations performed."""
        # Count transformations by type
        type_counts: Dict[str, int] = {}
        concept_mappings: Dict[str, int] = {}

        for entry in self._transformation_log:
            source_type = entry.get("source_type", "unknown")
            target_type = entry.get("target_type", "unknown")
            key = f"{source_type} -> {target_type}"
            type_counts[key] = type_counts.get(key, 0) + 1

            if entry.get("target_concept_id"):
                concept_mappings[source_type] = concept_mappings.get(source_type, 0) + 1

        return {
            "total_transformations": len(self._transformation_log),
            "unique_persons_created": len(self._token_to_person_id),
            "visits_created": self._visit_id_counter,
            "conditions_created": self._condition_id_counter,
            "measurements_created": self._measurement_id_counter,
            "drug_exposures_created": self._drug_id_counter,
            "transformation_types": type_counts,
            "successful_concept_mappings": concept_mappings,
            "omop_version": "5.4",
            "vocabularies_used": ["SNOMED", "LOINC", "RxNorm", "OMOP"],
        }

    def demonstrate_transformation(
        self,
        source_data: Dict,
        data_type: str,
    ) -> Dict:
        """
        Demonstrate the transformation of a single record.
        Shows before (source) and after (OMOP) formats.
        """
        result = {
            "source_format": source_data,
            "data_type": data_type,
            "omop_format": None,
            "mappings_applied": [],
        }

        if data_type == "patient":
            person = self.transform_patient_to_person(source_data)
            result["omop_format"] = person.model_dump()
            result["omop_table"] = "PERSON"
            result["mappings_applied"] = [
                f"Gender '{source_data.get('gender')}' -> concept_id {person.gender_concept_id}",
                f"Token -> person_source_value",
            ]

        elif data_type == "encounter":
            visit = self.transform_encounter_to_visit(source_data)
            result["omop_format"] = visit.model_dump()
            result["omop_table"] = "VISIT_OCCURRENCE"
            result["mappings_applied"] = [
                f"Type '{source_data.get('encounter_type')}' -> concept_id {visit.visit_concept_id}",
            ]

            # Also show condition transformation
            condition = self.transform_diagnosis_to_condition(source_data, visit.visit_occurrence_id)
            if condition:
                result["related_omop"] = {
                    "table": "CONDITION_OCCURRENCE",
                    "data": condition.model_dump(),
                }
                icd_code = self._extract_icd_code(source_data.get("admission_diagnosis", ""))
                result["mappings_applied"].append(
                    f"ICD-10 '{icd_code}' -> SNOMED concept_id {condition.condition_concept_id}"
                )

        elif data_type == "lab_result":
            measurement = self.transform_lab_to_measurement(source_data)
            if measurement:
                result["omop_format"] = measurement.model_dump()
                result["omop_table"] = "MEASUREMENT"
                result["mappings_applied"] = [
                    f"LOINC '{source_data.get('observation_code')}' -> concept_id {measurement.measurement_concept_id}",
                ]

        elif data_type == "medication":
            drug = self.transform_medication_to_drug_exposure(source_data)
            if drug:
                result["omop_format"] = drug.model_dump()
                result["omop_table"] = "DRUG_EXPOSURE"
                result["mappings_applied"] = [
                    f"RxNorm '{source_data.get('observation_code')}' -> concept_id {drug.drug_concept_id}",
                ]

        return result
