#!/usr/bin/env python3
"""
Generate a sample discharge summary PDF for the Medical Record Processing demo.
Uses reportlab to create a professional-looking medical document.
"""

import os
import sys

# Try to use reportlab, fall back to fpdf2 if not available
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    USE_REPORTLAB = True
except ImportError:
    USE_REPORTLAB = False
    try:
        from fpdf import FPDF
    except ImportError:
        print("Neither reportlab nor fpdf2 is installed.")
        print("Install with: pip install reportlab")
        sys.exit(1)


SAMPLE_DOCUMENT = """KING FAISAL SPECIALIST HOSPITAL & RESEARCH CENTRE (KFSHRC)
Department of Cardiology - Heart Centre
Al Faisal Medical City, MBC 16
P.O. Box 3354, Riyadh 11211, Kingdom of Saudi Arabia

DISCHARGE SUMMARY

Patient: Fatima Abdullah Al-Rashid
Date of Birth: March 15, 1958
National ID (Iqama): 1087654321
Medical Record Number: KFSH-2024-789456
Admission Date: January 15, 2024
Discharge Date: January 19, 2024

ATTENDING PHYSICIAN: Dr. Khalid Al-Habib, MD, FRCP
CARDIOLOGY CONSULTANT: Dr. Ahmed Al-Zahrani, MD, FACC

PATIENT CONTACT INFORMATION:
Address: Villa 45, Al-Malqa District, Riyadh 13524, Kingdom of Saudi Arabia
Phone: +966 11 555 0147
Mobile: +966 50 123 4567
Email: f.alrashid58@gmail.com
Emergency Contact: Mohammed Al-Rashid (son) - +966 50 987 6543

INSURANCE INFORMATION:
Health Plan ID: CCHI-SA-987654321
Group Number: BUPA-45678
Member ID: FAR-123456789
Employer: Ministry of Education (Retired)

CHIEF COMPLAINT:
66-year-old female presenting with acute onset chest pain and shortness of breath.

HISTORY OF PRESENT ILLNESS:
Mrs. Al-Rashid presented to the Emergency Department on January 15, 2024 at 14:32
with complaints of severe substernal chest pain radiating to her left arm,
associated with diaphoresis and dyspnea. Pain began approximately 2 hours prior
to arrival while she was at home in Al-Malqa District. She rated the pain as 9/10
in intensity. She has a history of type 2 diabetes mellitus, hypertension, and
hyperlipidemia.

PAST MEDICAL HISTORY:
1. Type 2 diabetes mellitus (T2DM) - diagnosed 2015
2. Essential hypertension (HTN) - diagnosed 2010
3. Hyperlipidemia - diagnosed 2012
4. Coronary artery disease - previous PCI in 2020

MEDICATIONS ON ADMISSION:
1. Metformin 1000mg PO twice daily
2. Lisinopril 20mg PO daily
3. Atorvastatin 40mg PO at bedtime
4. Aspirin 81mg PO daily
5. Amlodipine 5mg PO daily

ALLERGIES: Penicillin (rash), Sulfa drugs (hives)

SOCIAL HISTORY:
- Non-smoker
- No alcohol use
- Retired teacher (35 years with Ministry of Education)
- Lives with family

FAMILY HISTORY:
- Father: MI at age 62, deceased
- Mother: Type 2 diabetes, hypertension
- Brother: CABG at age 58

PHYSICAL EXAMINATION ON ADMISSION:
Vital Signs:
- Blood Pressure: 162/94 mmHg
- Heart Rate: 98 bpm
- Respiratory Rate: 22/min
- Temperature: 98.6F (37.0C)
- Oxygen Saturation: 94% on room air
- Weight: 78.5 kg
- Height: 165 cm

General: Anxious-appearing female in moderate distress
HEENT: Normocephalic, atraumatic
Cardiovascular: Tachycardic, regular rhythm, S1/S2 present, no murmurs
Pulmonary: Bilateral basilar crackles
Abdomen: Soft, non-tender, non-distended
Extremities: No edema, pulses 2+ bilaterally

LABORATORY DATA:

Admission Labs (January 15, 2024 15:00):
- Troponin I: 2.4 ng/mL (elevated, ref: <0.04)
- BNP: 450 pg/mL (elevated)
- Glucose: 186 mg/dL (elevated)
- HbA1c: 7.8% (elevated, ref: <5.7%)
- Creatinine: 1.1 mg/dL
- BUN: 18 mg/dL
- eGFR: 62 mL/min/1.73m2
- Sodium: 139 mEq/L
- Potassium: 4.2 mEq/L
- LDL Cholesterol: 142 mg/dL (elevated, ref: <100)
- HDL Cholesterol: 38 mg/dL (low)
- Triglycerides: 198 mg/dL (elevated)
- WBC: 11.2 x10^3/uL
- Hemoglobin: 12.8 g/dL
- Platelets: 245 x10^3/uL
- INR: 1.0

DIAGNOSTIC STUDIES:

1. ECG (January 15, 2024): Sinus tachycardia, ST-segment depression in leads
   V3-V6, consistent with anterolateral ischemia.

2. Chest X-ray (January 15, 2024): Mild pulmonary vascular congestion.
   No infiltrates or effusions.

3. Echocardiogram (January 16, 2024): LVEF 45% (mildly reduced), anterior
   wall hypokinesis, mild mitral regurgitation, no pericardial effusion.

4. Cardiac Catheterization (January 17, 2024):
   - 90% stenosis of LAD (Left Anterior Descending)
   - 60% stenosis of RCA (Right Coronary Artery)
   - Successful PCI with drug-eluting stent to LAD

HOSPITAL COURSE:
Mrs. Al-Rashid was admitted to the Cardiac Care Unit with a diagnosis of
Non-ST Elevation Myocardial Infarction (NSTEMI). She was started on dual
antiplatelet therapy (aspirin and clopidogrel), anticoagulation with heparin,
and high-intensity statin therapy. Beta-blocker was initiated after stabilization.

On hospital day 2, she underwent cardiac catheterization which revealed
significant LAD disease. Successful percutaneous coronary intervention (PCI)
with drug-eluting stent placement was performed. Post-procedure, she remained
hemodynamically stable with resolution of chest pain.

Blood glucose was monitored closely given her diabetes. She experienced mild
hyperglycemia requiring sliding scale insulin coverage in addition to her
home metformin.

DISCHARGE DIAGNOSES:
1. Non-ST Elevation Myocardial Infarction (NSTEMI) - I21.4
2. Coronary artery disease, status post PCI with stent - I25.10, Z95.5
3. Type 2 diabetes mellitus - E11.9
4. Essential hypertension - I10
5. Hyperlipidemia - E78.5

DISCHARGE MEDICATIONS:
1. Aspirin 81mg PO daily - continue indefinitely
2. Clopidogrel (Plavix) 75mg PO daily - continue for 12 months minimum
3. Atorvastatin 80mg PO at bedtime - increased from 40mg
4. Metoprolol succinate (Toprol-XL) 25mg PO daily - NEW
5. Lisinopril 20mg PO daily - continue
6. Metformin 1000mg PO twice daily - continue
7. Nitroglycerin 0.4mg SL PRN chest pain - NEW

DISCHARGE INSTRUCTIONS:
1. Follow up with Dr. Al-Habib (cardiology) in 1 week - call +966 11 464 7272 to schedule
2. Follow up with primary care physician Dr. Omar Al-Qahtani in 2 weeks
3. Cardiac rehabilitation referral - start in 2 weeks at KFSHRC Cardiac Rehab
4. Low sodium, heart-healthy diet
5. No strenuous activity for 2 weeks
6. Do not lift anything heavier than 5 kg for 1 week
7. Return to ED if experiencing chest pain, shortness of breath, palpitations,
   or bleeding at catheterization site

CONDITION AT DISCHARGE: Stable, improved

Electronically signed by:
Khalid Al-Habib, MD, FRCP
Attending Physician - Cardiology, Heart Centre
SCFHS License: SA-MD-123456
Saudi Commission ID: 9876543210
Date: January 19, 2024 10:30 AM

Dictated: 01/19/2024 09:15 by Dr. Khalid Al-Habib
Transcribed: 01/19/2024 10:00 by Medical Records Department
Document ID: DS-2024-KFSH-789456
IP Address: 192.168.1.100

KING FAISAL SPECIALIST HOSPITAL & RESEARCH CENTRE
This document contains protected personal information under PDPL
(Saudi Personal Data Protection Law)
"""


def create_pdf_with_reportlab(output_path: str):
    """Create PDF using reportlab."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=6,
        alignment=1,  # Center
        textColor=colors.HexColor('#2c5282')
    )

    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=11,
        spaceAfter=6,
        spaceBefore=12,
        textColor=colors.HexColor('#2d3748'),
        borderColor=colors.HexColor('#e2e8f0'),
        borderWidth=0,
        borderPadding=0,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        spaceAfter=4,
    )

    # Build document content
    story = []

    lines = SAMPLE_DOCUMENT.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue

        # Escape HTML special chars
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Detect headers
        if line.startswith('KING FAISAL') or line == 'DISCHARGE SUMMARY':
            story.append(Paragraph(line, title_style))
        elif line.endswith(':') and len(line) < 50 and line.isupper():
            story.append(Paragraph(f"<b>{line}</b>", header_style))
        elif line.startswith('Department of') or line.startswith('Al Faisal') or line.startswith('P.O. Box'):
            story.append(Paragraph(line, ParagraphStyle('Center', parent=body_style, alignment=1)))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
    print(f"PDF created successfully: {output_path}")


def create_pdf_with_fpdf(output_path: str):
    """Create PDF using fpdf2."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    lines = SAMPLE_DOCUMENT.strip().split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            pdf.ln(4)
            continue

        # Detect headers and format accordingly
        if line.startswith('KING FAISAL') or line == 'DISCHARGE SUMMARY':
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(44, 82, 130)
            pdf.cell(0, 8, line, ln=True, align='C')
        elif line.endswith(':') and len(line) < 50 and line.isupper():
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(45, 55, 72)
            pdf.ln(4)
            pdf.cell(0, 6, line, ln=True)
        elif line.startswith('Department of') or line.startswith('Al Faisal') or line.startswith('P.O. Box'):
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 5, line, ln=True, align='C')
        else:
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(0, 0, 0)
            # Handle long lines with multi_cell
            pdf.multi_cell(0, 5, line)

    pdf.output(output_path)
    print(f"PDF created successfully: {output_path}")


def main():
    # Determine output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_path = os.path.join(project_root, 'frontend', 'public', 'sample_discharge_summary_kfshrc.pdf')

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if USE_REPORTLAB:
        print("Using reportlab to generate PDF...")
        create_pdf_with_reportlab(output_path)
    else:
        print("Using fpdf2 to generate PDF...")
        create_pdf_with_fpdf(output_path)

    print(f"\nPDF saved to: {output_path}")
    print(f"File size: {os.path.getsize(output_path):,} bytes")


if __name__ == '__main__':
    main()
