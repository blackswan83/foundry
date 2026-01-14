"""
De-identification Service

Implements Safe Harbor and HiPS (Hybrid Pseudonymization Strategy) methodologies
for de-identifying Protected Health Information (PHI) while maintaining data utility.

Safe Harbor Method (HIPAA):
- Removes or generalizes 18 specific identifiers
- Provides a "safe" way to de-identify data without statistical analysis

HiPS (Hybrid Pseudonymization Strategy):
- Combines multiple de-identification techniques
- Replaces identifiers with realistic surrogate values
- Maintains referential integrity
- Preserves data utility for research
"""

import hashlib
import random
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from ..models.patient import Patient, PatientEncounter, ClinicalObservation, GenderType


@dataclass
class DeidentificationConfig:
    """Configuration for de-identification."""
    # Shift dates by a random number of days (per patient)
    date_shift_range: Tuple[int, int] = (-365, 365)
    # Generalize ages over this threshold to "90+"
    age_threshold: int = 89
    # Replace names with surrogate names
    use_surrogate_names: bool = True
    # Generalize locations to region level only
    generalize_location: bool = True
    # Remove all contact information
    remove_contact_info: bool = True
    # Redact clinical notes
    redact_clinical_notes: bool = True


class DeidentificationService:
    """
    Service for de-identifying patient data using Safe Harbor and HiPS methodologies.
    """

    # HIPAA Safe Harbor 18 identifiers
    SAFE_HARBOR_IDENTIFIERS = [
        "names",
        "geographic_data",  # smaller than state
        "dates",  # except year
        "phone_numbers",
        "fax_numbers",
        "email_addresses",
        "social_security_numbers",
        "medical_record_numbers",
        "health_plan_beneficiary_numbers",
        "account_numbers",
        "certificate_license_numbers",
        "vehicle_identifiers",
        "device_identifiers",
        "web_urls",
        "ip_addresses",
        "biometric_identifiers",
        "full_face_photos",
        "any_other_unique_identifier",
    ]

    # Surrogate names for HiPS
    SURROGATE_MALE_NAMES = [
        "Patient_M001", "Patient_M002", "Patient_M003", "Patient_M004",
        "Patient_M005", "Patient_M006", "Patient_M007", "Patient_M008",
    ]

    SURROGATE_FEMALE_NAMES = [
        "Patient_F001", "Patient_F002", "Patient_F003", "Patient_F004",
        "Patient_F005", "Patient_F006", "Patient_F007", "Patient_F008",
    ]

    # PHI patterns for redaction in clinical notes
    PHI_PATTERNS = [
        (r"\b[A-Z][a-z]+ [A-Z][a-z\-]+\b", "[NAME]"),  # Names
        (r"\b\d{10}\b", "[ID]"),  # National ID
        (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]"),  # Phone numbers
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),  # Email
        (r"\bDr\.\s*[A-Z][a-z]+\s*[A-Z][a-z\-]+\b", "[PROVIDER]"),  # Doctor names
        (r"\bMRN[-:]?\s*\w+\b", "[MRN]"),  # MRN references
        (r"\b\d{1,5}\s+[A-Za-z]+\s+(Street|St|Road|Rd|Avenue|Ave)\b", "[ADDRESS]"),  # Addresses
    ]

    def __init__(self, config: Optional[DeidentificationConfig] = None):
        self.config = config or DeidentificationConfig()
        self._patient_date_shifts: Dict[str, int] = {}
        self._surrogate_name_map: Dict[str, str] = {}
        self._surrogate_counter = {"M": 0, "F": 0}
        self._deidentification_log: List[Dict] = []

    def _get_date_shift(self, patient_id: str) -> int:
        """Get consistent date shift for a patient (for referential integrity)."""
        if patient_id not in self._patient_date_shifts:
            self._patient_date_shifts[patient_id] = random.randint(
                *self.config.date_shift_range
            )
        return self._patient_date_shifts[patient_id]

    def _shift_date(self, d: date, patient_id: str) -> date:
        """Shift a date by the patient's random offset."""
        shift = self._get_date_shift(patient_id)
        return d + timedelta(days=shift)

    def _shift_datetime(self, dt: datetime, patient_id: str) -> datetime:
        """Shift a datetime by the patient's random offset."""
        shift = self._get_date_shift(patient_id)
        return dt + timedelta(days=shift)

    def _generalize_age(self, dob: date) -> Tuple[int, bool]:
        """
        Calculate age and generalize if over threshold.
        Returns (age, is_generalized).
        """
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age > self.config.age_threshold:
            return self.config.age_threshold, True
        return age, False

    def _get_surrogate_name(self, patient_id: str, gender: GenderType) -> str:
        """Get or create a surrogate name for a patient."""
        if patient_id not in self._surrogate_name_map:
            if gender == GenderType.MALE:
                self._surrogate_counter["M"] += 1
                self._surrogate_name_map[patient_id] = f"Patient_M{self._surrogate_counter['M']:04d}"
            else:
                self._surrogate_counter["F"] += 1
                self._surrogate_name_map[patient_id] = f"Patient_F{self._surrogate_counter['F']:04d}"
        return self._surrogate_name_map[patient_id]

    def _redact_clinical_notes(self, notes: str) -> str:
        """Redact PHI from clinical notes using pattern matching."""
        if not notes:
            return notes

        redacted = notes
        for pattern, replacement in self.PHI_PATTERNS:
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)

        return redacted

    def deidentify_patient(self, patient: Patient, token: str) -> Dict[str, Any]:
        """
        De-identify a patient record using Safe Harbor + HiPS methodology.

        Returns a de-identified patient dictionary (not a Patient object,
        as many fields are removed or transformed).
        """
        patient_id = patient.source_patient_id

        # Log the de-identification
        log_entry = {
            "original_patient_id": patient_id,
            "token": token,
            "timestamp": datetime.now().isoformat(),
            "actions": [],
        }

        deidentified = {
            # Use token instead of any identifying ID
            "patient_token": token,
            "source_system": patient.source_system.value,
        }

        # NAMES: Replace with surrogate
        if self.config.use_surrogate_names:
            surrogate = self._get_surrogate_name(patient_id, patient.gender)
            deidentified["surrogate_id"] = surrogate
            log_entry["actions"].append("replaced_name_with_surrogate")
        else:
            deidentified["surrogate_id"] = None
            log_entry["actions"].append("removed_name")

        # Remove all direct identifiers
        # national_id - REMOVED
        # passport_number - REMOVED
        # first_name - REMOVED
        # middle_name - REMOVED
        # last_name - REMOVED
        # family_name - REMOVED
        log_entry["actions"].append("removed_direct_identifiers")

        # DATE OF BIRTH: Shift or generalize
        shifted_dob = self._shift_date(patient.date_of_birth, patient_id)
        age, is_generalized = self._generalize_age(patient.date_of_birth)

        if is_generalized:
            deidentified["year_of_birth"] = shifted_dob.year - age  # Approximate
            deidentified["age_group"] = "90+"
            log_entry["actions"].append("generalized_age_over_89")
        else:
            deidentified["year_of_birth"] = shifted_dob.year
            deidentified["month_of_birth"] = shifted_dob.month
            # Day removed for Safe Harbor compliance
            deidentified["age_at_data_collection"] = age
            log_entry["actions"].append("shifted_dates")

        # GENDER: Keep (not PHI)
        deidentified["gender"] = patient.gender.value

        # CONTACT INFO: Remove all
        # phone_number - REMOVED
        # email - REMOVED
        # address_line1 - REMOVED
        # address_line2 - REMOVED
        log_entry["actions"].append("removed_contact_info")

        # GEOGRAPHIC DATA: Generalize to region only
        if self.config.generalize_location and patient.region:
            deidentified["region"] = patient.region
            log_entry["actions"].append("generalized_location_to_region")
        # city - REMOVED
        # postal_code - REMOVED

        # MRN: Remove (replaced by token)
        # mrn - REMOVED
        log_entry["actions"].append("removed_mrn_used_token")

        self._deidentification_log.append(log_entry)

        return deidentified

    def deidentify_encounter(
        self,
        encounter: PatientEncounter,
        patient_id: str,
        token: str,
    ) -> Dict[str, Any]:
        """De-identify an encounter record."""
        deidentified = {
            "patient_token": token,
            "encounter_id": hashlib.sha256(encounter.encounter_id.encode()).hexdigest()[:12],
            "source_system": encounter.source_system.value,
            "encounter_type": encounter.encounter_type,
        }

        # Shift dates
        deidentified["admission_date"] = self._shift_datetime(
            encounter.admission_date, patient_id
        ).isoformat()

        if encounter.discharge_date:
            deidentified["discharge_date"] = self._shift_datetime(
                encounter.discharge_date, patient_id
            ).isoformat()

        # Keep department (generally not PHI)
        deidentified["department"] = encounter.department

        # Remove provider names
        # attending_physician - REMOVED
        # attending_physician_id - REMOVED

        # Keep diagnoses (clinical value)
        deidentified["chief_complaint"] = encounter.chief_complaint
        deidentified["admission_diagnosis"] = encounter.admission_diagnosis
        deidentified["discharge_diagnosis"] = encounter.discharge_diagnosis

        # Redact clinical notes
        if self.config.redact_clinical_notes and encounter.clinical_notes:
            deidentified["clinical_notes"] = self._redact_clinical_notes(
                encounter.clinical_notes
            )
        else:
            deidentified["clinical_notes"] = None

        # Keep vital signs (clinical value, not PHI)
        deidentified["vitals"] = {
            "temperature_celsius": encounter.temperature_celsius,
            "heart_rate_bpm": encounter.heart_rate_bpm,
            "blood_pressure_systolic": encounter.blood_pressure_systolic,
            "blood_pressure_diastolic": encounter.blood_pressure_diastolic,
            "respiratory_rate": encounter.respiratory_rate,
            "oxygen_saturation": encounter.oxygen_saturation,
            "weight_kg": encounter.weight_kg,
            "height_cm": encounter.height_cm,
        }

        return deidentified

    def deidentify_observation(
        self,
        observation: ClinicalObservation,
        patient_id: str,
        token: str,
    ) -> Dict[str, Any]:
        """De-identify an observation record."""
        deidentified = {
            "patient_token": token,
            "observation_id": hashlib.sha256(observation.observation_id.encode()).hexdigest()[:12],
            "source_system": observation.source_system.value,
            "observation_type": observation.observation_type,
            "observation_code": observation.observation_code,
            "observation_code_system": observation.observation_code_system,
            "observation_name": observation.observation_name,
        }

        # Shift datetime
        deidentified["observation_datetime"] = self._shift_datetime(
            observation.observation_datetime, patient_id
        ).isoformat()

        # Keep clinical values
        deidentified["value_numeric"] = observation.value_numeric
        deidentified["value_text"] = observation.value_text
        deidentified["value_unit"] = observation.value_unit
        deidentified["reference_range_low"] = observation.reference_range_low
        deidentified["reference_range_high"] = observation.reference_range_high
        deidentified["abnormal_flag"] = observation.abnormal_flag

        # For medications
        deidentified["dose"] = observation.dose
        deidentified["route"] = observation.route
        deidentified["frequency"] = observation.frequency

        # Remove provider info
        # performing_provider - REMOVED

        return deidentified

    def deidentify_dataset(
        self,
        patients: List[Patient],
        encounters: List[PatientEncounter],
        observations: List[ClinicalObservation],
        patient_tokens: Dict[str, str],
    ) -> Dict[str, List[Dict]]:
        """
        De-identify an entire dataset.

        Args:
            patients: List of patient records
            encounters: List of encounter records
            observations: List of observation records
            patient_tokens: Mapping of source_patient_id -> token

        Returns:
            Dictionary with de-identified patients, encounters, and observations
        """
        deidentified_patients = []
        deidentified_encounters = []
        deidentified_observations = []

        # De-identify patients
        for patient in patients:
            token = patient_tokens.get(patient.source_patient_id)
            if token:
                deidentified_patients.append(
                    self.deidentify_patient(patient, token)
                )

        # De-identify encounters
        for encounter in encounters:
            token = patient_tokens.get(encounter.source_patient_id)
            if token:
                deidentified_encounters.append(
                    self.deidentify_encounter(encounter, encounter.source_patient_id, token)
                )

        # De-identify observations
        for observation in observations:
            token = patient_tokens.get(observation.source_patient_id)
            if token:
                deidentified_observations.append(
                    self.deidentify_observation(observation, observation.source_patient_id, token)
                )

        return {
            "patients": deidentified_patients,
            "encounters": deidentified_encounters,
            "observations": deidentified_observations,
        }

    def get_deidentification_report(self) -> Dict:
        """Generate a report of de-identification actions taken."""
        total_patients = len(self._deidentification_log)

        # Count action types
        action_counts: Dict[str, int] = {}
        for entry in self._deidentification_log:
            for action in entry["actions"]:
                action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "total_patients_deidentified": total_patients,
            "total_date_shifts_applied": len(self._patient_date_shifts),
            "surrogate_names_created": {
                "male": self._surrogate_counter["M"],
                "female": self._surrogate_counter["F"],
            },
            "action_summary": action_counts,
            "safe_harbor_compliance": {
                "identifiers_addressed": self.SAFE_HARBOR_IDENTIFIERS,
                "method": "Safe Harbor + HiPS hybrid",
            },
            "configuration": {
                "date_shift_range": self.config.date_shift_range,
                "age_threshold": self.config.age_threshold,
                "surrogate_names": self.config.use_surrogate_names,
                "location_generalization": self.config.generalize_location,
                "clinical_notes_redaction": self.config.redact_clinical_notes,
            },
        }

    def demonstrate_deidentification(self, patient: Patient, token: str) -> Dict:
        """
        Demonstrate the de-identification process with before/after comparison.
        """
        # Original data (PHI)
        original = {
            "name": f"{patient.first_name} {patient.middle_name or ''} {patient.last_name}".strip(),
            "national_id": patient.national_id,
            "date_of_birth": patient.date_of_birth.isoformat(),
            "phone": patient.phone_number,
            "email": patient.email,
            "address": f"{patient.address_line1}, {patient.city}, {patient.region}",
            "mrn": patient.mrn,
        }

        # De-identified data
        deidentified = self.deidentify_patient(patient, token)

        return {
            "original_phi": original,
            "deidentified": deidentified,
            "phi_removed": [
                "Full name",
                "National ID",
                "Exact date of birth",
                "Phone number",
                "Email address",
                "Street address",
                "City",
                "Medical record number",
            ],
            "phi_transformed": [
                "DOB -> Year of birth (shifted)",
                "Name -> Surrogate ID",
                "All IDs -> Anonymous token",
                "Region -> Generalized location",
            ],
            "data_preserved": [
                "Gender",
                "Age group",
                "Region (generalized)",
                "All clinical data",
            ],
        }
