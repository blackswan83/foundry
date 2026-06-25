#!/usr/bin/env python3
"""
Generate a sample CSV with longitudinal multi-institute patient records for the Elembic demo.

Structure:
- 200 unique patients
- 3-7 encounters per patient across different Saudi healthcare institutes
- Same national_id for each patient (enables linkage)
- Different MRN per institute (shows fragmentation)
- ~1,000 total rows demonstrating cross-system patient matching
"""

import csv
import random
from datetime import datetime, date, timedelta
import sys
import os

# Saudi healthcare institutes with their MRN prefixes
INSTITUTES = {
    "KFSHRC": {"prefix": "KFH", "full_name": "King Faisal Specialist Hospital & Research Centre"},
    "Riyadh Military Hospital": {"prefix": "RMH", "full_name": "Prince Sultan Military Medical City"},
    "King Fahd Medical City": {"prefix": "KFMC", "full_name": "King Fahd Medical City"},
    "King Abdulaziz Medical City": {"prefix": "KAMC", "full_name": "King Abdulaziz Medical City"},
    "King Khalid University Hospital": {"prefix": "KKUH", "full_name": "King Khalid University Hospital"},
}

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

FAMILY_NAMES = [
    "Al-Saud", "Al-Rashid", "Al-Otaibi", "Al-Ghamdi", "Al-Qahtani",
    "Al-Shehri", "Al-Dosari", "Al-Harbi", "Al-Zahrani", "Al-Maliki",
    "Al-Yami", "Al-Shammari", "Al-Mutairi", "Al-Anazi", "Al-Juhani",
    "Al-Subai", "Al-Tamimi", "Al-Dawsari", "Al-Sulaiman", "Al-Khaldi",
    "Al-Amri", "Al-Thani", "Al-Salem", "Al-Faisal", "Al-Turki",
]

REGIONS_CITIES = {
    "Riyadh": ["Riyadh", "Al-Kharj", "Al-Majma'ah", "Al-Dawadmi"],
    "Makkah": ["Makkah", "Jeddah", "Taif", "Rabigh"],
    "Eastern Province": ["Dammam", "Dhahran", "Al-Khobar", "Jubail", "Qatif"],
    "Madinah": ["Madinah", "Yanbu", "Al-Ula"],
    "Asir": ["Abha", "Khamis Mushait", "Najran"],
    "Qassim": ["Buraidah", "Unaizah", "Al-Rass"],
}

# Diagnoses grouped by specialty (for realistic encounter sequences)
CHRONIC_CONDITIONS = [
    ("Type 2 diabetes mellitus", "E11.9"),
    ("Essential hypertension", "I10"),
    ("Chronic kidney disease", "N18.9"),
    ("Coronary artery disease", "I25.10"),
    ("Heart failure", "I50.9"),
    ("Atrial fibrillation", "I48.91"),
]

ONCOLOGY_CONDITIONS = [
    ("Acute lymphoblastic leukemia", "C91.0"),
    ("Breast cancer", "C50.9"),
    ("Colorectal cancer", "C18.9"),
    ("Non-Hodgkin lymphoma", "C85.9"),
    ("Multiple myeloma", "C90.0"),
    ("Hepatocellular carcinoma", "C22.0"),
]

ACUTE_CONDITIONS = [
    ("Pneumonia", "J18.9"),
    ("Acute kidney injury", "N17.9"),
    ("Stroke", "I63.9"),
    ("Myocardial infarction", "I21.9"),
    ("Pulmonary embolism", "I26.99"),
    ("Sepsis", "A41.9"),
]

FOLLOW_UP_REASONS = [
    ("Follow-up visit", "Z09"),
    ("Routine health examination", "Z00.00"),
    ("Medication review", "Z51.81"),
    ("Lab work monitoring", "Z01.812"),
]

DEPARTMENTS = {
    "chronic": ["Internal Medicine", "Cardiology", "Nephrology", "Endocrinology"],
    "oncology": ["Oncology", "Hematology", "Radiation Oncology", "Surgical Oncology"],
    "acute": ["Emergency Medicine", "ICU", "Internal Medicine", "Surgery"],
    "followup": ["Internal Medicine", "Outpatient Clinic", "Oncology", "Cardiology"],
}

STREETS = ["King Fahd", "King Abdullah", "Prince Sultan", "Tahlia", "Olaya", "Prince Mohammed", "King Faisal"]


def generate_national_id():
    """Generate a realistic Saudi National ID."""
    first_digit = random.choice(["1", "2"])
    remaining = "".join([str(random.randint(0, 9)) for _ in range(9)])
    return first_digit + remaining


def generate_phone():
    """Generate a Saudi phone number."""
    prefixes = ["050", "053", "054", "055", "056", "057", "058", "059"]
    prefix = random.choice(prefixes)
    number = "".join([str(random.randint(0, 9)) for _ in range(7)])
    return f"+966{prefix[1:]}{number}"


def generate_email(first_name, last_name):
    """Generate an email address."""
    domains = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]
    clean_last = last_name.lower().replace("al-", "").replace("-", "")
    return f"{first_name.lower()}.{clean_last}@{random.choice(domains)}"


def create_patient_profile(patient_idx):
    """Create a unique patient profile with demographics."""
    gender = random.choice(["M", "F"])

    if gender == "M":
        first_name = random.choice(MALE_FIRST_NAMES)
        middle_name = random.choice(MALE_FIRST_NAMES) if random.random() > 0.3 else ""
    else:
        first_name = random.choice(FEMALE_FIRST_NAMES)
        middle_name = random.choice(FEMALE_FIRST_NAMES) if random.random() > 0.3 else ""

    last_name = random.choice(FAMILY_NAMES)
    family_name = last_name.replace("Al-", "") if random.random() > 0.5 else ""

    # Age between 25 and 75 (more likely to have multiple encounters)
    age = random.randint(25, 75)
    dob = date.today() - timedelta(days=age * 365 + random.randint(0, 364))

    # Location
    region = random.choice(list(REGIONS_CITIES.keys()))
    city = random.choice(REGIONS_CITIES[region])

    # National ID stays the same across ALL institutes (this is the linkage key)
    national_id = generate_national_id()

    # Determine primary condition type for realistic encounter sequence
    condition_type = random.choices(
        ["chronic", "oncology", "mixed"],
        weights=[0.5, 0.3, 0.2]
    )[0]

    if condition_type == "chronic":
        primary_condition = random.choice(CHRONIC_CONDITIONS)
    elif condition_type == "oncology":
        primary_condition = random.choice(ONCOLOGY_CONDITIONS)
    else:
        primary_condition = random.choice(CHRONIC_CONDITIONS + ONCOLOGY_CONDITIONS)

    return {
        "patient_idx": patient_idx,
        "national_id": national_id,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "family_name": family_name,
        "date_of_birth": dob,
        "gender": gender,
        "phone_number": generate_phone(),
        "email": generate_email(first_name, last_name) if random.random() > 0.3 else "",
        "address": f"{random.randint(1, 9999)} {random.choice(STREETS)} Street",
        "city": city,
        "region": region,
        "postal_code": str(random.randint(10000, 99999)),
        "condition_type": condition_type,
        "primary_condition": primary_condition,
        "age": age,
        "mrns": {},  # Will be populated per-institute
    }


def generate_encounters_for_patient(patient):
    """Generate 3-7 encounters across different institutes for a patient."""
    encounters = []
    num_encounters = random.randint(3, 7)

    # Select institutes this patient will visit
    institutes_to_visit = random.sample(list(INSTITUTES.keys()), min(num_encounters, len(INSTITUTES)))

    # Generate timeline: spread encounters over 2-3 years
    start_date = datetime.now() - timedelta(days=random.randint(365, 1095))

    # Generate MRNs for each institute (DIFFERENT per institute - this shows fragmentation)
    for inst in institutes_to_visit:
        prefix = INSTITUTES[inst]["prefix"]
        patient["mrns"][inst] = f"{prefix}-{random.randint(100000, 999999)}"

    # First encounter: usually the initial diagnosis
    current_date = start_date

    for enc_idx in range(num_encounters):
        # Pick institute (with some repeats for follow-ups)
        if enc_idx < len(institutes_to_visit):
            institute = institutes_to_visit[enc_idx]
        else:
            institute = random.choice(institutes_to_visit)

        # Ensure we have an MRN for this institute
        if institute not in patient["mrns"]:
            prefix = INSTITUTES[institute]["prefix"]
            patient["mrns"][institute] = f"{prefix}-{random.randint(100000, 999999)}"

        # Determine encounter type based on position in timeline
        if enc_idx == 0:
            # First encounter: initial diagnosis
            encounter_type = random.choice(["inpatient", "emergency"])
            diagnosis = patient["primary_condition"]
            dept_type = patient["condition_type"] if patient["condition_type"] in DEPARTMENTS else "chronic"
            department = random.choice(DEPARTMENTS.get(dept_type, DEPARTMENTS["chronic"]))
        elif enc_idx == num_encounters - 1 or random.random() > 0.7:
            # Last or random: follow-up
            encounter_type = "outpatient"
            diagnosis = random.choice(FOLLOW_UP_REASONS)
            department = random.choice(DEPARTMENTS["followup"])
        else:
            # Middle encounters: mix of acute events and follow-ups
            if random.random() > 0.6:
                encounter_type = random.choice(["inpatient", "emergency"])
                diagnosis = random.choice(ACUTE_CONDITIONS + [patient["primary_condition"]])
                department = random.choice(DEPARTMENTS["acute"] + DEPARTMENTS.get(patient["condition_type"], []))
            else:
                encounter_type = "outpatient"
                diagnosis = random.choice([patient["primary_condition"]] + FOLLOW_UP_REASONS)
                department = random.choice(DEPARTMENTS["followup"])

        # Calculate dates
        admission_date = current_date
        if encounter_type == "outpatient":
            discharge_date = admission_date
        else:
            los_days = random.randint(1, 14) if encounter_type == "inpatient" else random.randint(0, 1)
            discharge_date = admission_date + timedelta(days=los_days)

        # Chief complaint
        chief_complaints = [
            diagnosis[0],
            "Chest pain", "Shortness of breath", "Abdominal pain",
            "Fatigue", "Fever", "Follow-up", "Lab monitoring",
        ]
        chief_complaint = random.choice(chief_complaints[:4]) if enc_idx == 0 else random.choice(chief_complaints)

        # Clinical notes
        gender_word = "male" if patient["gender"] == "M" else "female"
        clinical_notes = (
            f"{patient['age']}yo {gender_word} presenting with {chief_complaint}. "
            f"Patient seen at {institute}. "
            f"PMH: {patient['primary_condition'][0]}. "
            f"Assessment: {diagnosis[0]}. "
            f"Plan: {random.choice(['admit for workup', 'outpatient follow-up', 'continue current treatment', 'refer to specialist'])}."
        )

        encounter = {
            "source_system": institute,
            "patient_id": f"PAT-{patient['patient_idx']:06d}",
            "national_id": patient["national_id"],  # SAME across all encounters
            "mrn": patient["mrns"][institute],  # DIFFERENT per institute
            "first_name": patient["first_name"],
            "middle_name": patient["middle_name"],
            "last_name": patient["last_name"],
            "family_name": patient["family_name"],
            "date_of_birth": patient["date_of_birth"].strftime("%Y-%m-%d"),
            "gender": patient["gender"],
            "phone_number": patient["phone_number"],
            "email": patient["email"],
            "address_line1": patient["address"],
            "city": patient["city"],
            "region": patient["region"],
            "postal_code": patient["postal_code"],
            "encounter_id": f"ENC-{patient['patient_idx']:06d}-{enc_idx + 1:02d}",
            "encounter_type": encounter_type,
            "admission_date": admission_date.strftime("%Y-%m-%d"),
            "discharge_date": discharge_date.strftime("%Y-%m-%d"),
            "department": department,
            "diagnosis_code": diagnosis[1],
            "diagnosis_description": diagnosis[0],
            "chief_complaint": chief_complaint,
            "clinical_notes": clinical_notes,
        }

        encounters.append(encounter)

        # Move forward in time for next encounter
        current_date += timedelta(days=random.randint(30, 180))

    return encounters


def main():
    random.seed(42)  # For reproducibility

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "frontend", "public", "sample_patient_data.csv"
    )

    num_patients = 200
    print(f"Generating longitudinal data for {num_patients} patients...")
    print("Each patient will have 3-7 encounters across different Saudi healthcare institutes.")
    print("This demonstrates cross-system patient linkage via tokenization.\n")

    fieldnames = [
        "source_system", "patient_id", "national_id", "mrn",
        "first_name", "middle_name", "last_name", "family_name",
        "date_of_birth", "gender", "phone_number", "email",
        "address_line1", "city", "region", "postal_code",
        "encounter_id", "encounter_type", "admission_date", "discharge_date",
        "department", "diagnosis_code", "diagnosis_description",
        "chief_complaint", "clinical_notes"
    ]

    all_encounters = []

    for i in range(1, num_patients + 1):
        patient = create_patient_profile(i)
        encounters = generate_encounters_for_patient(patient)
        all_encounters.extend(encounters)

        if i % 50 == 0:
            print(f"  Generated {i} patients ({len(all_encounters)} total encounters)...")

    # Shuffle encounters to simulate real-world data collection
    random.shuffle(all_encounters)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for encounter in all_encounters:
            writer.writerow(encounter)

    print(f"\nDone! CSV saved to: {output_path}")
    print(f"Total patients: {num_patients}")
    print(f"Total encounters: {len(all_encounters)}")
    print(f"Average encounters per patient: {len(all_encounters) / num_patients:.1f}")
    print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")

    # Show institute distribution
    institute_counts = {}
    for enc in all_encounters:
        inst = enc["source_system"]
        institute_counts[inst] = institute_counts.get(inst, 0) + 1

    print("\nEncounters by institute:")
    for inst, count in sorted(institute_counts.items(), key=lambda x: -x[1]):
        print(f"  {inst}: {count}")


if __name__ == "__main__":
    main()
