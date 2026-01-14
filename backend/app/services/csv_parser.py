"""
CSV Parser Service

Parses uploaded CSV files containing patient data and converts them
to the internal data structures for processing through the de-identification pipeline.
"""

import csv
import io
import hashlib
import random
from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

from ..models.patient import Patient, PatientEncounter, SourceSystem, GenderType


@dataclass
class CSVParseResult:
    """Result of parsing a CSV file."""
    success: bool
    patients: List[Patient]
    encounters: List[PatientEncounter]
    errors: List[str]
    warnings: List[str]
    row_count: int
    valid_row_count: int


class CSVParserService:
    """
    Service for parsing CSV files containing patient data.
    Handles validation and conversion to internal data structures.
    """

    # Required columns (at minimum)
    REQUIRED_COLUMNS = [
        "first_name",
        "last_name",
        "date_of_birth",
        "gender",
    ]

    # Optional columns that will be parsed if present
    OPTIONAL_COLUMNS = [
        "patient_id", "national_id", "mrn", "middle_name", "family_name",
        "phone_number", "email", "address_line1", "city", "region", "postal_code",
        "encounter_id", "encounter_type", "admission_date", "discharge_date",
        "department", "diagnosis_code", "diagnosis_description",
        "chief_complaint", "clinical_notes",
    ]

    # Column name aliases (for flexibility)
    COLUMN_ALIASES = {
        "dob": "date_of_birth",
        "birth_date": "date_of_birth",
        "birthdate": "date_of_birth",
        "sex": "gender",
        "firstname": "first_name",
        "first": "first_name",
        "lastname": "last_name",
        "last": "last_name",
        "middlename": "middle_name",
        "middle": "middle_name",
        "familyname": "family_name",
        "phone": "phone_number",
        "telephone": "phone_number",
        "address": "address_line1",
        "street": "address_line1",
        "zipcode": "postal_code",
        "zip": "postal_code",
        "id": "patient_id",
        "national_id_number": "national_id",
        "nid": "national_id",
        "medical_record_number": "mrn",
        "diagnosis": "diagnosis_description",
        "icd_code": "diagnosis_code",
        "icd10": "diagnosis_code",
        "notes": "clinical_notes",
        "admit_date": "admission_date",
        "discharge": "discharge_date",
        "dept": "department",
    }

    def __init__(self):
        self._patient_counter = 0
        self._encounter_counter = 0
        random.seed(42)

    def _normalize_column_name(self, col: str) -> str:
        """Normalize column name to standard format."""
        normalized = col.lower().strip().replace(" ", "_").replace("-", "_")
        return self.COLUMN_ALIASES.get(normalized, normalized)

    def _parse_date(self, value: str) -> Optional[date]:
        """Parse various date formats."""
        if not value or value.strip() == "":
            return None

        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue

        return None

    def _parse_datetime(self, value: str) -> Optional[datetime]:
        """Parse various datetime formats."""
        if not value or value.strip() == "":
            return None

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue

        return None

    def _parse_gender(self, value: str) -> GenderType:
        """Parse gender value."""
        if not value:
            return GenderType.OTHER

        val = value.strip().upper()
        if val in ["M", "MALE", "MAN", "BOY"]:
            return GenderType.MALE
        elif val in ["F", "FEMALE", "WOMAN", "GIRL"]:
            return GenderType.FEMALE
        else:
            return GenderType.OTHER

    def _generate_patient_id(self) -> str:
        """Generate a unique patient ID."""
        self._patient_counter += 1
        return f"CSV-PAT-{self._patient_counter:08d}"

    def _generate_encounter_id(self) -> str:
        """Generate a unique encounter ID."""
        self._encounter_counter += 1
        return f"CSV-ENC-{self._encounter_counter:010d}"

    def parse_csv(self, csv_content: str) -> CSVParseResult:
        """
        Parse CSV content into Patient and Encounter objects.

        Args:
            csv_content: Raw CSV string content

        Returns:
            CSVParseResult with parsed data and any errors/warnings
        """
        errors = []
        warnings = []
        patients = []
        encounters = []
        row_count = 0
        valid_row_count = 0

        try:
            # Parse CSV
            reader = csv.DictReader(io.StringIO(csv_content))

            # Normalize column names
            if reader.fieldnames is None:
                return CSVParseResult(
                    success=False,
                    patients=[],
                    encounters=[],
                    errors=["CSV file is empty or has no headers"],
                    warnings=[],
                    row_count=0,
                    valid_row_count=0,
                )

            normalized_fieldnames = {
                orig: self._normalize_column_name(orig)
                for orig in reader.fieldnames
            }

            # Check for required columns
            available_columns = set(normalized_fieldnames.values())
            missing_required = [
                col for col in self.REQUIRED_COLUMNS
                if col not in available_columns
            ]

            if missing_required:
                return CSVParseResult(
                    success=False,
                    patients=[],
                    encounters=[],
                    errors=[f"Missing required columns: {', '.join(missing_required)}"],
                    warnings=[],
                    row_count=0,
                    valid_row_count=0,
                )

            # Process each row
            for row_idx, row in enumerate(reader, start=2):  # Start at 2 (1-indexed + header)
                row_count += 1

                try:
                    # Normalize row keys
                    normalized_row = {
                        normalized_fieldnames[k]: v
                        for k, v in row.items()
                        if k in normalized_fieldnames
                    }

                    # Parse patient data
                    patient, patient_errors = self._parse_patient_row(normalized_row, row_idx)
                    if patient_errors:
                        errors.extend(patient_errors)
                        continue

                    if patient:
                        patients.append(patient)

                        # Parse encounter data if present
                        encounter, enc_errors = self._parse_encounter_row(normalized_row, patient, row_idx)
                        if enc_errors:
                            warnings.extend(enc_errors)  # Encounter errors are warnings
                        if encounter:
                            encounters.append(encounter)

                        valid_row_count += 1

                except Exception as e:
                    errors.append(f"Row {row_idx}: Unexpected error - {str(e)}")

        except csv.Error as e:
            return CSVParseResult(
                success=False,
                patients=[],
                encounters=[],
                errors=[f"CSV parsing error: {str(e)}"],
                warnings=[],
                row_count=0,
                valid_row_count=0,
            )

        # Add summary warnings
        if len(patients) == 0:
            errors.append("No valid patient records found in CSV")

        success = len(errors) == 0 or valid_row_count > 0

        return CSVParseResult(
            success=success,
            patients=patients,
            encounters=encounters,
            errors=errors,
            warnings=warnings,
            row_count=row_count,
            valid_row_count=valid_row_count,
        )

    def _parse_patient_row(
        self,
        row: Dict[str, str],
        row_idx: int
    ) -> Tuple[Optional[Patient], List[str]]:
        """Parse a single row into a Patient object."""
        errors = []

        # Required fields
        first_name = row.get("first_name", "").strip()
        last_name = row.get("last_name", "").strip()
        dob_str = row.get("date_of_birth", "").strip()
        gender_str = row.get("gender", "").strip()

        if not first_name:
            errors.append(f"Row {row_idx}: Missing first_name")
        if not last_name:
            errors.append(f"Row {row_idx}: Missing last_name")

        dob = self._parse_date(dob_str)
        if not dob:
            errors.append(f"Row {row_idx}: Invalid or missing date_of_birth '{dob_str}'")

        if errors:
            return None, errors

        # Parse optional fields
        gender = self._parse_gender(gender_str)
        patient_id = row.get("patient_id", "").strip() or self._generate_patient_id()

        try:
            patient = Patient(
                source_system=SourceSystem.HIS,  # Default to HIS for uploaded data
                source_patient_id=patient_id,
                national_id=row.get("national_id", "").strip() or None,
                first_name=first_name,
                middle_name=row.get("middle_name", "").strip() or None,
                last_name=last_name,
                family_name=row.get("family_name", "").strip() or None,
                date_of_birth=dob,
                gender=gender,
                phone_number=row.get("phone_number", "").strip() or None,
                email=row.get("email", "").strip() or None,
                address_line1=row.get("address_line1", "").strip() or None,
                city=row.get("city", "").strip() or None,
                region=row.get("region", "").strip() or None,
                postal_code=row.get("postal_code", "").strip() or None,
                mrn=row.get("mrn", "").strip() or None,
            )
            return patient, []
        except Exception as e:
            return None, [f"Row {row_idx}: Error creating patient - {str(e)}"]

    def _parse_encounter_row(
        self,
        row: Dict[str, str],
        patient: Patient,
        row_idx: int,
    ) -> Tuple[Optional[PatientEncounter], List[str]]:
        """Parse encounter data from a row if present."""
        warnings = []

        # Check if encounter data is present
        has_encounter_data = any([
            row.get("encounter_id"),
            row.get("encounter_type"),
            row.get("admission_date"),
            row.get("department"),
            row.get("diagnosis_code"),
            row.get("diagnosis_description"),
        ])

        if not has_encounter_data:
            return None, []

        # Parse admission date (required for encounter)
        admission_date_str = row.get("admission_date", "").strip()
        admission_date = self._parse_datetime(admission_date_str)

        if not admission_date:
            # Use current date as default
            admission_date = datetime.now()
            warnings.append(f"Row {row_idx}: Missing admission_date, using current date")

        # Parse discharge date if present
        discharge_date_str = row.get("discharge_date", "").strip()
        discharge_date = self._parse_datetime(discharge_date_str) if discharge_date_str else None

        # Build diagnosis string
        diagnosis_desc = row.get("diagnosis_description", "").strip()
        diagnosis_code = row.get("diagnosis_code", "").strip()
        if diagnosis_code and diagnosis_desc:
            full_diagnosis = f"{diagnosis_desc} ({diagnosis_code})"
        elif diagnosis_desc:
            full_diagnosis = diagnosis_desc
        elif diagnosis_code:
            full_diagnosis = f"ICD: {diagnosis_code}"
        else:
            full_diagnosis = "Not specified"

        try:
            encounter = PatientEncounter(
                encounter_id=row.get("encounter_id", "").strip() or self._generate_encounter_id(),
                source_system=patient.source_system,
                source_patient_id=patient.source_patient_id,
                encounter_type=row.get("encounter_type", "").strip() or "outpatient",
                admission_date=admission_date,
                discharge_date=discharge_date,
                department=row.get("department", "").strip() or "General",
                chief_complaint=row.get("chief_complaint", "").strip() or diagnosis_desc or "Not specified",
                admission_diagnosis=full_diagnosis,
                discharge_diagnosis=full_diagnosis if discharge_date else None,
                clinical_notes=row.get("clinical_notes", "").strip() or None,
            )
            return encounter, warnings
        except Exception as e:
            return None, [f"Row {row_idx}: Error creating encounter - {str(e)}"]


def generate_deidentified_csv(
    deidentified_patients: List[Dict[str, Any]],
    deidentified_encounters: List[Dict[str, Any]],
) -> str:
    """
    Generate a CSV string from de-identified data.

    Args:
        deidentified_patients: List of de-identified patient records
        deidentified_encounters: List of de-identified encounter records

    Returns:
        CSV string content
    """
    output = io.StringIO()

    # Define output columns
    fieldnames = [
        "patient_token",
        "surrogate_id",
        "gender",
        "year_of_birth",
        "month_of_birth",
        "age_at_data_collection",
        "region",
        "source_system",
        # Encounter fields (if available)
        "encounter_id",
        "encounter_type",
        "admission_date",
        "discharge_date",
        "department",
        "chief_complaint",
        "admission_diagnosis",
        "clinical_notes",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()

    # Create patient lookup
    patient_lookup = {p["patient_token"]: p for p in deidentified_patients}

    if deidentified_encounters:
        # Write one row per encounter, including patient data
        for encounter in deidentified_encounters:
            token = encounter.get("patient_token")
            patient = patient_lookup.get(token, {})

            row = {**patient, **encounter}
            writer.writerow(row)
    else:
        # Write just patient data
        for patient in deidentified_patients:
            writer.writerow(patient)

    return output.getvalue()
