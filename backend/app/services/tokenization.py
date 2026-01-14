"""
Tokenization Service for Cross-System Patient Linkage

Implements privacy-preserving patient linkage using cryptographic tokens.
This enables building longitudinal patient records across multiple hospital
systems while maintaining complete anonymity.
"""

import hashlib
import hmac
import secrets
from datetime import datetime, date
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field

from ..models.patient import Patient, PatientEncounter, ClinicalObservation, LinkedPatientRecord


@dataclass
class TokenizationConfig:
    """Configuration for the tokenization service."""
    # Secret key for HMAC-based tokenization (in production, this would be securely managed)
    secret_key: bytes = field(default_factory=lambda: secrets.token_bytes(32))
    # Algorithm for hashing
    hash_algorithm: str = "sha256"
    # Whether to use salted hashing
    use_salt: bool = True
    # Salt for additional security
    salt: bytes = field(default_factory=lambda: secrets.token_bytes(16))


class TokenizationService:
    """
    Service for creating privacy-preserving patient tokens for cross-system linkage.

    The tokenization approach:
    1. Extract identifying attributes (National ID, DOB, Name components)
    2. Normalize and clean the attributes
    3. Apply cryptographic hashing with HMAC
    4. Generate a unique, irreversible token

    This enables:
    - Linking records from different systems for the same patient
    - No ability to reverse the token to identify the patient
    - Consistent tokens for the same patient across systems
    """

    def __init__(self, config: Optional[TokenizationConfig] = None):
        self.config = config or TokenizationConfig()
        self._token_registry: Dict[str, Set[str]] = {}  # token -> set of source_patient_ids
        self._patient_id_to_token: Dict[str, str] = {}  # source_patient_id -> token

    def _normalize_string(self, value: Optional[str]) -> str:
        """Normalize a string for consistent tokenization."""
        if value is None:
            return ""
        # Convert to uppercase, remove special characters, strip whitespace
        normalized = value.upper().strip()
        # Remove common prefixes that might vary
        normalized = normalized.replace("AL-", "").replace("AL ", "")
        # Remove spaces and hyphens
        normalized = normalized.replace(" ", "").replace("-", "")
        return normalized

    def _normalize_date(self, d: date) -> str:
        """Normalize a date for consistent tokenization."""
        return d.strftime("%Y%m%d")

    def _create_composite_key(self, patient: Patient) -> str:
        """
        Create a composite key from patient identifying attributes.

        Uses multiple attributes to improve matching accuracy:
        - National ID (most reliable)
        - Date of birth
        - First name + Last name (normalized)
        """
        components = []

        # Primary identifier: National ID
        if patient.national_id:
            components.append(f"NID:{patient.national_id}")

        # Secondary: Date of birth
        components.append(f"DOB:{self._normalize_date(patient.date_of_birth)}")

        # Tertiary: Name components
        first_name = self._normalize_string(patient.first_name)
        last_name = self._normalize_string(patient.last_name)
        components.append(f"NAME:{first_name}{last_name}")

        # Gender
        components.append(f"GEN:{patient.gender.value}")

        return "|".join(components)

    def generate_token(self, patient: Patient) -> str:
        """
        Generate a unique, privacy-preserving token for a patient.

        The token is:
        - Deterministic: Same patient always gets the same token
        - Irreversible: Cannot derive patient identity from token
        - Collision-resistant: Different patients get different tokens
        """
        # Create composite key from identifying attributes
        composite_key = self._create_composite_key(patient)

        # Apply HMAC for secure hashing
        if self.config.use_salt:
            key_with_salt = self.config.salt + composite_key.encode("utf-8")
        else:
            key_with_salt = composite_key.encode("utf-8")

        token_hash = hmac.new(
            self.config.secret_key,
            key_with_salt,
            self.config.hash_algorithm
        ).hexdigest()

        # Create a readable token format
        token = f"PT-{token_hash[:16].upper()}"

        # Register the token
        if token not in self._token_registry:
            self._token_registry[token] = set()
        self._token_registry[token].add(patient.source_patient_id)
        self._patient_id_to_token[patient.source_patient_id] = token

        return token

    def get_token_for_patient(self, source_patient_id: str) -> Optional[str]:
        """Get the token for a previously tokenized patient."""
        return self._patient_id_to_token.get(source_patient_id)

    def get_linked_patient_ids(self, token: str) -> Set[str]:
        """Get all source patient IDs linked to a token."""
        return self._token_registry.get(token, set())

    def tokenize_patient_batch(self, patients: List[Patient]) -> Dict[str, str]:
        """
        Tokenize a batch of patients.
        Returns a mapping of source_patient_id -> token.
        """
        return {patient.source_patient_id: self.generate_token(patient) for patient in patients}

    def link_patient_records(
        self,
        patients: List[Patient],
        encounters: List[PatientEncounter],
        observations: List[ClinicalObservation],
    ) -> List[LinkedPatientRecord]:
        """
        Link patient records from multiple systems using tokenization.

        This is the core functionality for demonstrating cross-system patient linkage.
        """
        # Step 1: Generate tokens for all patients
        patient_tokens = self.tokenize_patient_batch(patients)

        # Step 2: Group by token to find linked records
        token_to_patients: Dict[str, List[Patient]] = {}
        for patient in patients:
            token = patient_tokens[patient.source_patient_id]
            if token not in token_to_patients:
                token_to_patients[token] = []
            token_to_patients[token].append(patient)

        # Step 3: Create LinkedPatientRecord for each unique token
        linked_records = []

        for token, linked_patients in token_to_patients.items():
            # Get all source patient IDs for this token
            source_ids = {p.source_patient_id for p in linked_patients}

            # Find encounters for these patients
            patient_encounters = [
                enc for enc in encounters
                if enc.source_patient_id in source_ids
            ]

            # Find observations for these patients
            patient_observations = [
                obs for obs in observations
                if obs.source_patient_id in source_ids
            ]

            # Calculate date ranges
            all_dates = []
            for p in linked_patients:
                all_dates.append(p.date_of_birth)
            for enc in patient_encounters:
                all_dates.append(enc.admission_date.date())

            # Create source record references
            source_records = [
                {
                    "source_system": p.source_system.value,
                    "source_patient_id": p.source_patient_id,
                    "mrn": p.mrn,
                }
                for p in linked_patients
            ]

            # Determine source systems
            source_systems = {p.source_system.value for p in linked_patients}

            linked_record = LinkedPatientRecord(
                patient_token=token,
                source_records=source_records,
                encounters=patient_encounters,
                observations=patient_observations,
                earliest_record_date=min(all_dates) if all_dates else None,
                latest_record_date=max(all_dates) if all_dates else None,
                total_encounters=len(patient_encounters),
                source_systems_count=len(source_systems),
            )
            linked_records.append(linked_record)

        return linked_records

    def get_linkage_statistics(self) -> Dict:
        """Get statistics about the current tokenization state."""
        total_tokens = len(self._token_registry)
        total_records = sum(len(ids) for ids in self._token_registry.values())

        # Count tokens with multiple linked records
        multi_linked = sum(1 for ids in self._token_registry.values() if len(ids) > 1)

        # Distribution of links per token
        link_distribution = {}
        for ids in self._token_registry.values():
            count = len(ids)
            link_distribution[count] = link_distribution.get(count, 0) + 1

        return {
            "total_unique_tokens": total_tokens,
            "total_patient_records": total_records,
            "patients_with_multi_system_records": multi_linked,
            "average_records_per_patient": round(total_records / total_tokens, 2) if total_tokens > 0 else 0,
            "link_distribution": link_distribution,
        }

    def demonstrate_linkage(self, patients: List[Patient]) -> Dict:
        """
        Demonstrate the tokenization and linkage process.
        Returns detailed information about how patients were linked.
        """
        # Tokenize all patients
        tokens = self.tokenize_patient_batch(patients)

        # Group by token
        token_groups: Dict[str, List[Dict]] = {}
        for patient in patients:
            token = tokens[patient.source_patient_id]
            if token not in token_groups:
                token_groups[token] = []
            token_groups[token].append({
                "source_system": patient.source_system.value,
                "source_patient_id": patient.source_patient_id,
                "mrn": patient.mrn,
                "name": f"{patient.first_name} {patient.last_name}",
                "dob": patient.date_of_birth.isoformat(),
            })

        # Identify linked records
        linked = {
            token: records
            for token, records in token_groups.items()
            if len(records) > 1
        }

        return {
            "total_patient_records": len(patients),
            "unique_patients_identified": len(token_groups),
            "patients_with_linked_records": len(linked),
            "linked_record_details": linked,
            "statistics": self.get_linkage_statistics(),
        }
