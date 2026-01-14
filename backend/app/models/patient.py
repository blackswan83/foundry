"""
Source patient data models representing raw clinical data from multiple hospital systems.
These models represent the fragmented, unstructured data before transformation.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class GenderType(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class SourceSystem(str, Enum):
    """Simulated hospital source systems at KFSHRC"""
    HIS = "HIS"  # Hospital Information System
    LAB = "LAB"  # Laboratory System
    RAD = "RAD"  # Radiology System
    PHARMACY = "PHARMACY"  # Pharmacy System
    EMR = "EMR"  # Electronic Medical Records
    ICU = "ICU"  # ICU Monitoring System


class Patient(BaseModel):
    """
    Raw patient record from a source system.
    Contains PHI that will be de-identified.
    """
    source_system: SourceSystem
    source_patient_id: str  # Original ID in source system

    # PHI Fields (to be de-identified)
    national_id: Optional[str] = None  # Saudi National ID
    passport_number: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    family_name: Optional[str] = None  # Saudi family name

    date_of_birth: date
    gender: GenderType

    # Contact Information (PHI)
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None  # Saudi region
    postal_code: Optional[str] = None

    # Medical identifiers
    mrn: Optional[str] = None  # Medical Record Number

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PatientEncounter(BaseModel):
    """
    Clinical encounter/visit from a source system.
    """
    encounter_id: str
    source_system: SourceSystem
    source_patient_id: str

    encounter_type: str  # inpatient, outpatient, emergency, etc.
    admission_date: datetime
    discharge_date: Optional[datetime] = None

    department: Optional[str] = None
    attending_physician: Optional[str] = None  # PHI - name
    attending_physician_id: Optional[str] = None

    chief_complaint: Optional[str] = None
    admission_diagnosis: Optional[str] = None
    discharge_diagnosis: Optional[str] = None

    # Free text clinical notes (unstructured)
    clinical_notes: Optional[str] = None

    # Vital signs at admission
    temperature_celsius: Optional[float] = None
    heart_rate_bpm: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None


class ClinicalObservation(BaseModel):
    """
    Individual clinical observation or measurement.
    """
    observation_id: str
    source_system: SourceSystem
    source_patient_id: str
    encounter_id: Optional[str] = None

    observation_type: str  # lab_result, vital_sign, diagnosis, procedure, medication
    observation_code: Optional[str] = None  # LOINC, SNOMED, ICD-10, etc.
    observation_code_system: Optional[str] = None
    observation_name: str

    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_unit: Optional[str] = None

    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None
    abnormal_flag: Optional[str] = None

    observation_datetime: datetime
    performing_provider: Optional[str] = None  # PHI

    # For medications
    dose: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None


class LinkedPatientRecord(BaseModel):
    """
    Represents a patient linked across multiple source systems using tokenization.
    """
    patient_token: str  # Anonymous token for cross-system linkage
    source_records: List[dict]  # References to source patient records
    encounters: List[PatientEncounter] = []
    observations: List[ClinicalObservation] = []

    # Computed from all source records
    earliest_record_date: Optional[date] = None
    latest_record_date: Optional[date] = None
    total_encounters: int = 0
    source_systems_count: int = 0
