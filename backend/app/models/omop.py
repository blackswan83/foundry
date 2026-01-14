"""
OMOP Common Data Model (CDM) v5.4 compliant data models.
These represent the standardized, research-ready output format.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class Person(BaseModel):
    """OMOP CDM Person table - core demographic information."""
    person_id: int
    gender_concept_id: int  # OMOP concept: 8507=Male, 8532=Female
    year_of_birth: int
    month_of_birth: Optional[int] = None
    day_of_birth: Optional[int] = None
    birth_datetime: Optional[datetime] = None

    race_concept_id: int = 0  # 0 = No matching concept
    ethnicity_concept_id: int = 0

    location_id: Optional[int] = None
    provider_id: Optional[int] = None
    care_site_id: Optional[int] = None

    # Source values (de-identified references)
    person_source_value: Optional[str] = None  # Token, not original ID
    gender_source_value: Optional[str] = None
    race_source_value: Optional[str] = None
    ethnicity_source_value: Optional[str] = None


class VisitOccurrence(BaseModel):
    """OMOP CDM Visit Occurrence - clinical encounters."""
    visit_occurrence_id: int
    person_id: int

    visit_concept_id: int  # 9201=Inpatient, 9202=Outpatient, 9203=ER
    visit_start_date: date
    visit_start_datetime: Optional[datetime] = None
    visit_end_date: date
    visit_end_datetime: Optional[datetime] = None

    visit_type_concept_id: int = 44818518  # Visit derived from EHR

    provider_id: Optional[int] = None
    care_site_id: Optional[int] = None

    visit_source_value: Optional[str] = None
    visit_source_concept_id: int = 0

    admitted_from_concept_id: int = 0
    admitted_from_source_value: Optional[str] = None
    discharged_to_concept_id: int = 0
    discharged_to_source_value: Optional[str] = None

    preceding_visit_occurrence_id: Optional[int] = None


class ConditionOccurrence(BaseModel):
    """OMOP CDM Condition Occurrence - diagnoses and conditions."""
    condition_occurrence_id: int
    person_id: int

    condition_concept_id: int  # SNOMED concept ID
    condition_start_date: date
    condition_start_datetime: Optional[datetime] = None
    condition_end_date: Optional[date] = None
    condition_end_datetime: Optional[datetime] = None

    condition_type_concept_id: int = 32817  # EHR problem list
    condition_status_concept_id: int = 0

    stop_reason: Optional[str] = None
    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None

    condition_source_value: Optional[str] = None
    condition_source_concept_id: int = 0
    condition_status_source_value: Optional[str] = None


class Measurement(BaseModel):
    """OMOP CDM Measurement - lab results and vital signs."""
    measurement_id: int
    person_id: int

    measurement_concept_id: int  # LOINC concept ID
    measurement_date: date
    measurement_datetime: Optional[datetime] = None
    measurement_time: Optional[str] = None

    measurement_type_concept_id: int = 44818702  # Lab result

    operator_concept_id: int = 0
    value_as_number: Optional[float] = None
    value_as_concept_id: int = 0

    unit_concept_id: int = 0
    unit_source_value: Optional[str] = None

    range_low: Optional[float] = None
    range_high: Optional[float] = None

    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None

    measurement_source_value: Optional[str] = None
    measurement_source_concept_id: int = 0

    value_source_value: Optional[str] = None


class Observation(BaseModel):
    """OMOP CDM Observation - other clinical observations."""
    observation_id: int
    person_id: int

    observation_concept_id: int
    observation_date: date
    observation_datetime: Optional[datetime] = None

    observation_type_concept_id: int = 38000280  # Observation recorded from EHR

    value_as_number: Optional[float] = None
    value_as_string: Optional[str] = None
    value_as_concept_id: int = 0

    qualifier_concept_id: int = 0
    unit_concept_id: int = 0

    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None

    observation_source_value: Optional[str] = None
    observation_source_concept_id: int = 0

    unit_source_value: Optional[str] = None
    qualifier_source_value: Optional[str] = None
    value_source_value: Optional[str] = None
    observation_event_id: Optional[int] = None


class DrugExposure(BaseModel):
    """OMOP CDM Drug Exposure - medications."""
    drug_exposure_id: int
    person_id: int

    drug_concept_id: int  # RxNorm concept ID
    drug_exposure_start_date: date
    drug_exposure_start_datetime: Optional[datetime] = None
    drug_exposure_end_date: date
    drug_exposure_end_datetime: Optional[datetime] = None

    verbatim_end_date: Optional[date] = None
    drug_type_concept_id: int = 38000177  # Prescription written

    stop_reason: Optional[str] = None
    refills: Optional[int] = None
    quantity: Optional[float] = None
    days_supply: Optional[int] = None
    sig: Optional[str] = None  # Prescription instructions

    route_concept_id: int = 0
    lot_number: Optional[str] = None

    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None

    drug_source_value: Optional[str] = None
    drug_source_concept_id: int = 0
    route_source_value: Optional[str] = None
    dose_unit_source_value: Optional[str] = None


class ProcedureOccurrence(BaseModel):
    """OMOP CDM Procedure Occurrence - clinical procedures."""
    procedure_occurrence_id: int
    person_id: int

    procedure_concept_id: int  # SNOMED/CPT concept ID
    procedure_date: date
    procedure_datetime: Optional[datetime] = None
    procedure_end_date: Optional[date] = None
    procedure_end_datetime: Optional[datetime] = None

    procedure_type_concept_id: int = 38000275  # EHR order

    modifier_concept_id: int = 0
    quantity: Optional[int] = None

    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None

    procedure_source_value: Optional[str] = None
    procedure_source_concept_id: int = 0
    modifier_source_value: Optional[str] = None
