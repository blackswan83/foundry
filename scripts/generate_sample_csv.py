#!/usr/bin/env python3
"""
Generate a sample CSV with 1,000 fake Saudi patient records for the Foundry demo.
"""

import csv
import random
from datetime import datetime, date, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    "Jazan": ["Jazan", "Sabya", "Abu Arish"],
    "Qassim": ["Buraidah", "Unaizah", "Al-Rass"],
    "Tabuk": ["Tabuk", "Duba", "Tayma"],
    "Hail": ["Hail", "Baqaa"],
    "Northern Borders": ["Arar", "Rafha"],
}

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

DEPARTMENTS = [
    "Internal Medicine", "Oncology", "Hematology", "Nephrology",
    "Cardiology", "Gastroenterology", "Pulmonology", "Neurology",
    "Surgery", "Orthopedics", "Transplant Medicine", "ICU",
    "Emergency Medicine", "Pediatrics", "Obstetrics & Gynecology",
]

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


def generate_patient_record(patient_id):
    """Generate a single patient record."""
    gender = random.choice(["M", "F"])

    if gender == "M":
        first_name = random.choice(MALE_FIRST_NAMES)
        middle_name = random.choice(MALE_FIRST_NAMES) if random.random() > 0.3 else ""
    else:
        first_name = random.choice(FEMALE_FIRST_NAMES)
        middle_name = random.choice(FEMALE_FIRST_NAMES) if random.random() > 0.3 else ""

    last_name = random.choice(FAMILY_NAMES)
    family_name = last_name.replace("Al-", "") if random.random() > 0.5 else ""

    # Age between 18 and 85
    age = random.randint(18, 85)
    dob = date.today() - timedelta(days=age * 365 + random.randint(0, 364))

    # Location
    region = random.choice(list(REGIONS_CITIES.keys()))
    city = random.choice(REGIONS_CITIES[region])

    # Encounter info
    encounter_type = random.choice(["inpatient", "outpatient", "emergency"])
    days_ago = random.randint(1, 365)
    admission_date = datetime.now() - timedelta(days=days_ago)

    if encounter_type == "outpatient":
        discharge_date = admission_date
        los_days = 0
    else:
        los_days = random.randint(1, 14)
        discharge_date = admission_date + timedelta(days=los_days)

    # Diagnosis
    diagnosis_desc, diagnosis_code = random.choice(DIAGNOSES)

    # Chief complaint (sometimes same as diagnosis, sometimes more general)
    chief_complaints = [
        diagnosis_desc,
        "Chest pain",
        "Shortness of breath",
        "Abdominal pain",
        "Fatigue",
        "Fever",
        "Back pain",
        "Headache",
        "Nausea and vomiting",
        "Dizziness",
    ]
    chief_complaint = random.choice(chief_complaints)

    # Clinical notes
    gender_word = "male" if gender == "M" else "female"
    clinical_notes = (
        f"{age}yo {gender_word} presenting with {chief_complaint}. "
        f"Patient reports symptoms for {random.randint(1, 14)} days. "
        f"PMH: {random.choice(['diabetes', 'hypertension', 'CAD', 'none significant'])}. "
        f"Assessment: {diagnosis_desc}. Plan: {random.choice(['admit for workup', 'outpatient follow-up', 'discharge with medications'])}."
    )

    return {
        "patient_id": f"PAT-{patient_id:06d}",
        "national_id": generate_national_id(),
        "mrn": f"MRN-{random.randint(100000, 9999999)}",
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "family_name": family_name,
        "date_of_birth": dob.strftime("%Y-%m-%d"),
        "gender": gender,
        "phone_number": generate_phone(),
        "email": generate_email(first_name, last_name) if random.random() > 0.3 else "",
        "address_line1": f"{random.randint(1, 9999)} {random.choice(STREETS)} Street",
        "city": city,
        "region": region,
        "postal_code": str(random.randint(10000, 99999)),
        "encounter_id": f"ENC-{patient_id:06d}-{random.randint(1, 99):02d}",
        "encounter_type": encounter_type,
        "admission_date": admission_date.strftime("%Y-%m-%d"),
        "discharge_date": discharge_date.strftime("%Y-%m-%d") if discharge_date else "",
        "department": random.choice(DEPARTMENTS),
        "diagnosis_code": diagnosis_code,
        "diagnosis_description": diagnosis_desc,
        "chief_complaint": chief_complaint,
        "clinical_notes": clinical_notes,
    }


def main():
    random.seed(42)  # For reproducibility

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "frontend", "public", "sample_patient_data.csv"
    )

    print(f"Generating 1,000 patient records...")

    fieldnames = [
        "patient_id", "national_id", "mrn", "first_name", "middle_name",
        "last_name", "family_name", "date_of_birth", "gender", "phone_number",
        "email", "address_line1", "city", "region", "postal_code",
        "encounter_id", "encounter_type", "admission_date", "discharge_date",
        "department", "diagnosis_code", "diagnosis_description",
        "chief_complaint", "clinical_notes"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, 1001):
            record = generate_patient_record(i)
            writer.writerow(record)

            if i % 100 == 0:
                print(f"  Generated {i} records...")

    print(f"Done! CSV saved to: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
