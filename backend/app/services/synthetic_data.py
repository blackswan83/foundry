"""
Synthetic Saudi Patient Data Generator

Generates realistic synthetic patient data relevant to Saudi Arabia and KFSHRC,
including Saudi names, National IDs, regional addresses, and common medical conditions.
"""

import random
import hashlib
from datetime import datetime, date, timedelta
from typing import List, Tuple, Optional
from faker import Faker

from ..models.patient import (
    Patient,
    PatientEncounter,
    ClinicalObservation,
    SourceSystem,
    GenderType,
)


class SyntheticDataGenerator:
    """Generates synthetic Saudi-relevant patient data for demo purposes."""

    # Saudi first names
    MALE_FIRST_NAMES = [
        "Mohammed", "Abdullah", "Abdulrahman", "Fahd", "Khalid", "Salman",
        "Faisal", "Turki", "Nasser", "Sultan", "Bandar", "Saud", "Ahmed",
        "Omar", "Ali", "Hassan", "Hussein", "Youssef", "Ibrahim", "Hamad",
        "Nawaf", "Mishal", "Waleed", "Talal", "Mansour", "Majed", "Saeed",
    ]

    FEMALE_FIRST_NAMES = [
        "Fatima", "Noura", "Sara", "Lama", "Maha", "Haya", "Reem", "Dalal",
        "Amal", "Asma", "Nadia", "Layla", "Mariam", "Hind", "Abeer", "Ghada",
        "Salma", "Haifa", "Arwa", "Noor", "Jana", "Lina", "Malak", "Shahad",
    ]

    # Saudi family names
    FAMILY_NAMES = [
        "Al-Saud", "Al-Rashid", "Al-Otaibi", "Al-Ghamdi", "Al-Qahtani",
        "Al-Shehri", "Al-Dosari", "Al-Harbi", "Al-Zahrani", "Al-Maliki",
        "Al-Yami", "Al-Shammari", "Al-Mutairi", "Al-Anazi", "Al-Juhani",
        "Al-Subai", "Al-Tamimi", "Al-Dawsari", "Al-Sulaiman", "Al-Khaldi",
        "Al-Amri", "Al-Thani", "Al-Salem", "Al-Faisal", "Al-Turki",
    ]

    # Saudi regions and cities
    REGIONS_CITIES = {
        "Riyadh": ["Riyadh", "Al-Kharj", "Al-Majma'ah", "Al-Dawadmi"],
        "Makkah": ["Makkah", "Jeddah", "Taif", "Rabigh"],
        "Eastern Province": ["Dammam", "Dhahran", "Al-Khobar", "Jubail", "Qatif"],
        "Madinah": ["Madinah", "Yanbu", "Al-Ula"],
        "Asir": ["Abha", "Khamis Mushait", "Najran"],
        "Jazan": ["Jazan", "Sabya", "Abu Arish"],
        "Qassim": ["Buraidah", "Unaizah", "Al-Rass"],
        "Tabuk": ["Tabuk", "Duba", "Tayma"],
        "Hail": ["Hail", "Baqaa"],
        "Northern Borders": ["Arar", "Rafha"],
    }

    # Common diagnoses seen at KFSHRC (tertiary care center)
    DIAGNOSES = [
        ("Acute lymphoblastic leukemia", "C91.0"),
        ("Breast cancer", "C50.9"),
        ("Chronic kidney disease", "N18.9"),
        ("Type 2 diabetes mellitus", "E11.9"),
        ("Essential hypertension", "I10"),
        ("Coronary artery disease", "I25.10"),
        ("Heart failure", "I50.9"),
        ("Liver cirrhosis", "K74.60"),
        ("End-stage renal disease", "N18.6"),
        ("Sickle cell disease", "D57.1"),
        ("Thalassemia major", "D56.1"),
        ("Hepatocellular carcinoma", "C22.0"),
        ("Colorectal cancer", "C18.9"),
        ("Non-Hodgkin lymphoma", "C85.9"),
        ("Multiple myeloma", "C90.0"),
        ("Bone marrow transplant status", "Z94.81"),
        ("Kidney transplant status", "Z94.0"),
        ("Liver transplant status", "Z94.4"),
        ("Pneumonia", "J18.9"),
        ("Sepsis", "A41.9"),
        ("Acute kidney injury", "N17.9"),
        ("Stroke", "I63.9"),
        ("Myocardial infarction", "I21.9"),
        ("Pulmonary embolism", "I26.99"),
        ("Deep vein thrombosis", "I82.40"),
    ]

    # Lab tests
    LAB_TESTS = [
        ("Hemoglobin", "718-7", "g/dL", 12.0, 17.5),
        ("White blood cell count", "6690-2", "10*9/L", 4.5, 11.0),
        ("Platelet count", "777-3", "10*9/L", 150.0, 400.0),
        ("Creatinine", "2160-0", "mg/dL", 0.7, 1.3),
        ("Blood urea nitrogen", "3094-0", "mg/dL", 7.0, 20.0),
        ("Glucose", "2345-7", "mg/dL", 70.0, 100.0),
        ("HbA1c", "4548-4", "%", 4.0, 6.0),
        ("Sodium", "2951-2", "mEq/L", 136.0, 145.0),
        ("Potassium", "2823-3", "mEq/L", 3.5, 5.0),
        ("ALT", "1742-6", "U/L", 7.0, 56.0),
        ("AST", "1920-8", "U/L", 10.0, 40.0),
        ("Bilirubin total", "1975-2", "mg/dL", 0.1, 1.2),
        ("Albumin", "1751-7", "g/dL", 3.5, 5.5),
        ("Prothrombin time", "5902-2", "sec", 11.0, 13.5),
        ("INR", "6301-6", "ratio", 0.9, 1.1),
    ]

    # Medications
    MEDICATIONS = [
        ("Metformin", "860975", "500mg", "oral", "twice daily"),
        ("Lisinopril", "314076", "10mg", "oral", "once daily"),
        ("Atorvastatin", "617311", "20mg", "oral", "once daily"),
        ("Amlodipine", "329528", "5mg", "oral", "once daily"),
        ("Omeprazole", "904453", "20mg", "oral", "once daily"),
        ("Aspirin", "1191", "81mg", "oral", "once daily"),
        ("Insulin glargine", "847230", "varies", "subcutaneous", "once daily"),
        ("Furosemide", "4603", "40mg", "oral", "once daily"),
        ("Warfarin", "11289", "varies", "oral", "once daily"),
        ("Tacrolimus", "42316", "varies", "oral", "twice daily"),
        ("Mycophenolate", "68149", "500mg", "oral", "twice daily"),
        ("Filgrastim", "227718", "varies", "subcutaneous", "as needed"),
        ("Ondansetron", "26225", "4mg", "IV", "as needed"),
        ("Morphine", "7052", "varies", "IV", "as needed"),
    ]

    DEPARTMENTS = [
        "Internal Medicine", "Oncology", "Hematology", "Nephrology",
        "Cardiology", "Gastroenterology", "Pulmonology", "Neurology",
        "Surgery", "Orthopedics", "Transplant Medicine", "ICU",
        "Emergency Medicine", "Pediatrics", "Obstetrics & Gynecology",
    ]

    def __init__(self, seed: int = 42):
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
        self._patient_counter = 0
        self._encounter_counter = 0
        self._observation_counter = 0

    def _generate_national_id(self) -> str:
        """Generate a realistic-looking Saudi National ID (10 digits starting with 1 or 2)."""
        first_digit = random.choice(["1", "2"])  # 1 for Saudi, 2 for resident
        remaining = "".join([str(random.randint(0, 9)) for _ in range(9)])
        return first_digit + remaining

    def _generate_mrn(self, system: SourceSystem) -> str:
        """Generate a Medical Record Number for a specific system."""
        prefix = system.value[:3]
        number = str(random.randint(100000, 9999999))
        return f"{prefix}-{number}"

    def _generate_phone(self) -> str:
        """Generate a Saudi phone number."""
        prefixes = ["050", "053", "054", "055", "056", "057", "058", "059"]
        prefix = random.choice(prefixes)
        number = "".join([str(random.randint(0, 9)) for _ in range(7)])
        return f"+966{prefix[1:]}{number}"

    def _generate_email(self, first_name: str, last_name: str) -> str:
        """Generate an email address."""
        domains = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]
        return f"{first_name.lower()}.{last_name.lower().replace('Al-', '').replace('-', '')}@{random.choice(domains)}"

    def generate_patient(
        self,
        source_system: Optional[SourceSystem] = None,
        gender: Optional[GenderType] = None,
        age_range: Tuple[int, int] = (18, 85),
    ) -> Patient:
        """Generate a single synthetic patient."""
        self._patient_counter += 1

        if source_system is None:
            source_system = random.choice(list(SourceSystem))

        if gender is None:
            gender = random.choice([GenderType.MALE, GenderType.FEMALE])

        # Select name based on gender
        if gender == GenderType.MALE:
            first_name = random.choice(self.MALE_FIRST_NAMES)
            middle_name = random.choice(self.MALE_FIRST_NAMES)
        else:
            first_name = random.choice(self.FEMALE_FIRST_NAMES)
            middle_name = random.choice(self.FEMALE_FIRST_NAMES)

        last_name = random.choice(self.FAMILY_NAMES)

        # Generate date of birth
        age = random.randint(*age_range)
        dob = date.today() - timedelta(days=age * 365 + random.randint(0, 364))

        # Select region and city
        region = random.choice(list(self.REGIONS_CITIES.keys()))
        city = random.choice(self.REGIONS_CITIES[region])

        return Patient(
            source_system=source_system,
            source_patient_id=f"{source_system.value}-{self._patient_counter:08d}",
            national_id=self._generate_national_id(),
            passport_number=f"SA{random.randint(10000000, 99999999)}" if random.random() > 0.7 else None,
            first_name=first_name,
            middle_name=middle_name if random.random() > 0.3 else None,
            last_name=last_name,
            family_name=last_name.replace("Al-", "") if random.random() > 0.5 else None,
            date_of_birth=dob,
            gender=gender,
            phone_number=self._generate_phone(),
            email=self._generate_email(first_name, last_name) if random.random() > 0.4 else None,
            address_line1=f"{random.randint(1, 9999)} {random.choice(['King Fahd', 'King Abdullah', 'Prince Sultan', 'Tahlia', 'Olaya'])} Street",
            city=city,
            region=region,
            postal_code=str(random.randint(10000, 99999)),
            mrn=self._generate_mrn(source_system),
        )

    def generate_encounter(
        self,
        patient: Patient,
        encounter_date: Optional[datetime] = None,
    ) -> PatientEncounter:
        """Generate a clinical encounter for a patient."""
        self._encounter_counter += 1

        if encounter_date is None:
            days_ago = random.randint(0, 365 * 2)
            encounter_date = datetime.now() - timedelta(days=days_ago)

        encounter_type = random.choice(["inpatient", "outpatient", "emergency"])
        los_days = 0 if encounter_type == "outpatient" else random.randint(1, 21)

        discharge_date = encounter_date + timedelta(days=los_days) if los_days > 0 else None

        # Select diagnosis
        diagnosis, icd_code = random.choice(self.DIAGNOSES)

        # Generate attending physician name
        physician_first = random.choice(self.MALE_FIRST_NAMES + self.FEMALE_FIRST_NAMES)
        physician_last = random.choice(self.FAMILY_NAMES)

        # Generate realistic clinical notes
        notes = self._generate_clinical_notes(patient, diagnosis, encounter_type)

        return PatientEncounter(
            encounter_id=f"ENC-{self._encounter_counter:010d}",
            source_system=patient.source_system,
            source_patient_id=patient.source_patient_id,
            encounter_type=encounter_type,
            admission_date=encounter_date,
            discharge_date=discharge_date,
            department=random.choice(self.DEPARTMENTS),
            attending_physician=f"Dr. {physician_first} {physician_last}",
            attending_physician_id=f"PHYS-{random.randint(1000, 9999)}",
            chief_complaint=diagnosis,
            admission_diagnosis=f"{diagnosis} ({icd_code})",
            discharge_diagnosis=f"{diagnosis} ({icd_code})" if discharge_date else None,
            clinical_notes=notes,
            temperature_celsius=round(random.uniform(36.0, 39.0), 1),
            heart_rate_bpm=random.randint(60, 110),
            blood_pressure_systolic=random.randint(100, 180),
            blood_pressure_diastolic=random.randint(60, 100),
            respiratory_rate=random.randint(12, 24),
            oxygen_saturation=round(random.uniform(92.0, 100.0), 1),
            weight_kg=round(random.uniform(50.0, 120.0), 1),
            height_cm=round(random.uniform(150.0, 190.0), 1),
        )

    def _generate_clinical_notes(
        self,
        patient: Patient,
        diagnosis: str,
        encounter_type: str,
    ) -> str:
        """Generate realistic free-text clinical notes."""
        age = (date.today() - patient.date_of_birth).days // 365
        gender_word = "male" if patient.gender == GenderType.MALE else "female"

        templates = [
            f"Patient is a {age}-year-old {gender_word} presenting with {diagnosis}. "
            f"Patient reports symptoms for the past {random.randint(1, 14)} days. "
            f"PMH includes {random.choice(['diabetes', 'hypertension', 'no significant history'])}. "
            f"Physical examination reveals {random.choice(['stable vital signs', 'mild distress', 'normal findings'])}. "
            f"Plan: Admit for further workup and management.",

            f"{age}yo {gender_word[0].upper()} with h/o {random.choice(['DM', 'HTN', 'CAD', 'CKD', 'none'])} "
            f"presenting with {diagnosis}. Patient states symptoms began {random.randint(1, 7)} days ago. "
            f"Vitals stable on admission. Labs pending. "
            f"Will start treatment per protocol.",

            f"CC: {diagnosis}\n"
            f"HPI: {patient.first_name} {patient.last_name} is a {age}yo {gender_word} who presents today with {diagnosis}. "
            f"The patient describes {random.choice(['worsening symptoms', 'acute onset', 'gradual progression'])} over the past week. "
            f"ROS: {random.choice(['Positive for fatigue and malaise', 'Negative except as noted above', 'Positive for pain'])}. "
            f"Assessment: {diagnosis}. Plan: {random.choice(['Admit', 'Outpatient follow-up', 'Urgent workup'])}.",
        ]

        return random.choice(templates)

    def generate_lab_results(
        self,
        patient: Patient,
        encounter: PatientEncounter,
        num_tests: int = 5,
    ) -> List[ClinicalObservation]:
        """Generate lab results for an encounter."""
        observations = []
        selected_tests = random.sample(self.LAB_TESTS, min(num_tests, len(self.LAB_TESTS)))

        for test_name, loinc_code, unit, ref_low, ref_high in selected_tests:
            self._observation_counter += 1

            # Generate value - sometimes abnormal
            if random.random() > 0.7:
                # Abnormal value
                if random.random() > 0.5:
                    value = ref_high * random.uniform(1.1, 2.0)  # High
                    abnormal_flag = "H"
                else:
                    value = ref_low * random.uniform(0.3, 0.9)  # Low
                    abnormal_flag = "L"
            else:
                # Normal value
                value = random.uniform(ref_low, ref_high)
                abnormal_flag = None

            observations.append(
                ClinicalObservation(
                    observation_id=f"OBS-{self._observation_counter:012d}",
                    source_system=SourceSystem.LAB,
                    source_patient_id=patient.source_patient_id,
                    encounter_id=encounter.encounter_id,
                    observation_type="lab_result",
                    observation_code=loinc_code,
                    observation_code_system="LOINC",
                    observation_name=test_name,
                    value_numeric=round(value, 2),
                    value_unit=unit,
                    reference_range_low=ref_low,
                    reference_range_high=ref_high,
                    abnormal_flag=abnormal_flag,
                    observation_datetime=encounter.admission_date + timedelta(hours=random.randint(1, 24)),
                )
            )

        return observations

    def generate_medications(
        self,
        patient: Patient,
        encounter: PatientEncounter,
        num_meds: int = 3,
    ) -> List[ClinicalObservation]:
        """Generate medication orders for an encounter."""
        observations = []
        selected_meds = random.sample(self.MEDICATIONS, min(num_meds, len(self.MEDICATIONS)))

        for med_name, rxnorm, dose, route, frequency in selected_meds:
            self._observation_counter += 1

            observations.append(
                ClinicalObservation(
                    observation_id=f"OBS-{self._observation_counter:012d}",
                    source_system=SourceSystem.PHARMACY,
                    source_patient_id=patient.source_patient_id,
                    encounter_id=encounter.encounter_id,
                    observation_type="medication",
                    observation_code=rxnorm,
                    observation_code_system="RxNorm",
                    observation_name=med_name,
                    value_text=f"{dose} {route} {frequency}",
                    dose=dose,
                    route=route,
                    frequency=frequency,
                    observation_datetime=encounter.admission_date,
                )
            )

        return observations

    def generate_complete_patient_record(
        self,
        num_encounters: int = 3,
    ) -> Tuple[Patient, List[PatientEncounter], List[ClinicalObservation]]:
        """Generate a complete patient record with encounters and observations."""
        patient = self.generate_patient()
        encounters = []
        all_observations = []

        for i in range(num_encounters):
            # Space encounters over time
            days_ago = (num_encounters - i) * random.randint(30, 180)
            encounter_date = datetime.now() - timedelta(days=days_ago)

            encounter = self.generate_encounter(patient, encounter_date)
            encounters.append(encounter)

            # Generate observations for each encounter
            labs = self.generate_lab_results(patient, encounter)
            meds = self.generate_medications(patient, encounter)
            all_observations.extend(labs)
            all_observations.extend(meds)

        return patient, encounters, all_observations

    def generate_multi_system_patient(
        self,
    ) -> Tuple[List[Patient], List[PatientEncounter], List[ClinicalObservation]]:
        """
        Generate the same patient appearing in multiple hospital systems.
        This simulates fragmented records that need to be linked.
        """
        # Generate base patient info (same person)
        base_patient = self.generate_patient(source_system=SourceSystem.HIS)

        patients = []
        encounters = []
        observations = []

        # Create records in different systems with slight variations
        systems = [SourceSystem.HIS, SourceSystem.LAB, SourceSystem.EMR, SourceSystem.PHARMACY]

        for system in systems:
            # Copy patient data with system-specific ID
            self._patient_counter += 1
            patient_copy = Patient(
                source_system=system,
                source_patient_id=f"{system.value}-{self._patient_counter:08d}",
                national_id=base_patient.national_id,  # Same person - same ID
                first_name=base_patient.first_name,
                middle_name=base_patient.middle_name,
                last_name=base_patient.last_name,
                family_name=base_patient.family_name,
                date_of_birth=base_patient.date_of_birth,
                gender=base_patient.gender,
                phone_number=base_patient.phone_number,
                email=base_patient.email,
                address_line1=base_patient.address_line1,
                city=base_patient.city,
                region=base_patient.region,
                postal_code=base_patient.postal_code,
                mrn=self._generate_mrn(system),  # Different MRN per system
            )
            patients.append(patient_copy)

            # Generate encounters and observations
            enc = self.generate_encounter(patient_copy)
            encounters.append(enc)

            if system == SourceSystem.LAB:
                labs = self.generate_lab_results(patient_copy, enc, num_tests=8)
                observations.extend(labs)
            elif system == SourceSystem.PHARMACY:
                meds = self.generate_medications(patient_copy, enc, num_meds=5)
                observations.extend(meds)

        return patients, encounters, observations

    def generate_demo_dataset(
        self,
        num_single_system_patients: int = 20,
        num_multi_system_patients: int = 10,
    ) -> dict:
        """
        Generate a complete demo dataset.
        Returns a dictionary with all patients, encounters, and observations.
        """
        all_patients = []
        all_encounters = []
        all_observations = []

        # Generate single-system patients
        for _ in range(num_single_system_patients):
            patient, encounters, observations = self.generate_complete_patient_record()
            all_patients.append(patient)
            all_encounters.extend(encounters)
            all_observations.extend(observations)

        # Generate multi-system patients (fragmented records)
        for _ in range(num_multi_system_patients):
            patients, encounters, observations = self.generate_multi_system_patient()
            all_patients.extend(patients)
            all_encounters.extend(encounters)
            all_observations.extend(observations)

        return {
            "patients": all_patients,
            "encounters": all_encounters,
            "observations": all_observations,
            "summary": {
                "total_patient_records": len(all_patients),
                "unique_individuals": num_single_system_patients + num_multi_system_patients,
                "total_encounters": len(all_encounters),
                "total_observations": len(all_observations),
                "source_systems": len(SourceSystem),
            },
        }
