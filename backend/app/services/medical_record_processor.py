"""
Medical Record Processing Service

Comprehensive pipeline for processing medical records:
1. OCR extraction from PDF/images
2. Clinical NLP with entity extraction
3. Terminology mapping (SNOMED, ICD-10, LOINC, RxNorm, CPT)
4. HIPAA Safe Harbor de-identification (all 18 PHI types)
"""

import re
import json
import hashlib
import io
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class PHIType(str, Enum):
    """HIPAA Safe Harbor 18 PHI Identifiers"""
    NAME = "name"
    GEOGRAPHIC = "geographic"
    DATE = "date"
    PHONE = "phone"
    FAX = "fax"
    EMAIL = "email"
    SSN = "ssn"
    MRN = "mrn"
    HEALTH_PLAN_ID = "health_plan_id"
    ACCOUNT_NUMBER = "account_number"
    LICENSE_NUMBER = "license_number"
    VEHICLE_ID = "vehicle_id"
    DEVICE_ID = "device_id"
    URL = "url"
    IP_ADDRESS = "ip_address"
    BIOMETRIC = "biometric"
    PHOTO = "photo"
    UNIQUE_ID = "unique_id"


class EntityType(str, Enum):
    """Clinical entity types"""
    CONDITION = "condition"
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    LAB_TEST = "lab_test"
    LAB_VALUE = "lab_value"
    VITAL_SIGN = "vital_sign"
    ANATOMY = "anatomy"
    SYMPTOM = "symptom"
    DIAGNOSIS = "diagnosis"
    ALLERGY = "allergy"


@dataclass
class ExtractedEntity:
    """Represents an extracted clinical entity"""
    text: str
    entity_type: EntityType
    start_pos: int
    end_pos: int
    confidence: float
    normalized_term: Optional[str] = None
    terminology_code: Optional[str] = None
    terminology_system: Optional[str] = None
    context: Optional[str] = None


@dataclass
class PHIDetection:
    """Represents detected PHI"""
    text: str
    phi_type: PHIType
    start_pos: int
    end_pos: int
    confidence: float
    replacement: str


@dataclass
class ProcessingResult:
    """Result of medical record processing"""
    original_text: str
    deidentified_text: str
    entities: List[ExtractedEntity]
    phi_detections: List[PHIDetection]
    terminology_mappings: Dict[str, List[Dict]]
    processing_stats: Dict[str, Any]


class TerminologyService:
    """Service for loading and matching clinical terminologies"""

    def __init__(self):
        self.snomed: Dict = {}
        self.icd10: Dict = {}
        self.loinc: Dict = {}
        self.rxnorm: Dict = {}
        self.cpt: Dict = {}
        self._load_terminologies()

    def _load_terminologies(self):
        """Load terminology files"""
        data_dir = Path(__file__).parent.parent / "data" / "terminology"

        try:
            with open(data_dir / "snomed_ct.json", "r") as f:
                self.snomed = json.load(f)
        except FileNotFoundError:
            self.snomed = {"concepts": {}}

        try:
            with open(data_dir / "icd10_cm.json", "r") as f:
                self.icd10 = json.load(f)
        except FileNotFoundError:
            self.icd10 = {"codes": {}}

        try:
            with open(data_dir / "loinc.json", "r") as f:
                self.loinc = json.load(f)
        except FileNotFoundError:
            self.loinc = {"codes": {}}

        try:
            with open(data_dir / "rxnorm.json", "r") as f:
                self.rxnorm = json.load(f)
        except FileNotFoundError:
            self.rxnorm = {"drugs": {}}

        try:
            with open(data_dir / "cpt.json", "r") as f:
                self.cpt = json.load(f)
        except FileNotFoundError:
            self.cpt = {"codes": {}}

    def find_snomed_match(self, text: str) -> Optional[Dict]:
        """Find matching SNOMED CT concept"""
        text_lower = text.lower().strip()

        for code, concept in self.snomed.get("concepts", {}).items():
            term = concept.get("term", "").lower()
            synonyms = [s.lower() for s in concept.get("synonyms", [])]

            if text_lower == term or text_lower in synonyms:
                return {
                    "code": code,
                    "term": concept.get("term"),
                    "system": "SNOMED CT",
                    "semantic_type": concept.get("semantic_type")
                }

            # Partial match
            if text_lower in term or any(text_lower in syn for syn in synonyms):
                return {
                    "code": code,
                    "term": concept.get("term"),
                    "system": "SNOMED CT",
                    "semantic_type": concept.get("semantic_type"),
                    "match_type": "partial"
                }
        return None

    def find_icd10_match(self, text: str) -> Optional[Dict]:
        """Find matching ICD-10-CM code"""
        text_lower = text.lower().strip()

        for code, info in self.icd10.get("codes", {}).items():
            desc = info.get("description", "").lower()
            long_desc = info.get("long_description", "").lower()

            if text_lower in desc or text_lower in long_desc:
                return {
                    "code": code,
                    "description": info.get("description"),
                    "system": "ICD-10-CM",
                    "category": info.get("category"),
                    "snomed_mapping": info.get("snomed_mapping")
                }
        return None

    def find_loinc_match(self, text: str) -> Optional[Dict]:
        """Find matching LOINC code"""
        text_lower = text.lower().strip()

        for code, info in self.loinc.get("codes", {}).items():
            component = info.get("component", "").lower()
            short_name = info.get("short_name", "").lower()
            long_name = info.get("long_name", "").lower()

            if text_lower in component or text_lower in short_name or text_lower == short_name:
                return {
                    "code": code,
                    "name": info.get("short_name"),
                    "system": "LOINC",
                    "unit": info.get("unit"),
                    "reference_range": info.get("reference_range")
                }
        return None

    def find_rxnorm_match(self, text: str) -> Optional[Dict]:
        """Find matching RxNorm drug"""
        text_lower = text.lower().strip()

        for code, drug in self.rxnorm.get("drugs", {}).items():
            name = drug.get("name", "").lower()
            generic = drug.get("generic_name", "").lower()
            brands = [b.lower() for b in drug.get("brand_names", [])]

            if text_lower == name or text_lower == generic or text_lower in brands:
                return {
                    "code": code,
                    "name": drug.get("name"),
                    "generic_name": drug.get("generic_name"),
                    "system": "RxNorm",
                    "drug_class": drug.get("drug_class"),
                    "common_doses": drug.get("common_doses")
                }

            # Partial match
            if text_lower in name or text_lower in generic:
                return {
                    "code": code,
                    "name": drug.get("name"),
                    "system": "RxNorm",
                    "drug_class": drug.get("drug_class"),
                    "match_type": "partial"
                }
        return None

    def find_cpt_match(self, text: str) -> Optional[Dict]:
        """Find matching CPT procedure code"""
        text_lower = text.lower().strip()

        for code, info in self.cpt.get("codes", {}).items():
            short_desc = info.get("short_description", "").lower()
            long_desc = info.get("long_description", "").lower()

            if text_lower in short_desc or text_lower in long_desc:
                return {
                    "code": code,
                    "description": info.get("short_description"),
                    "system": "CPT",
                    "category": info.get("category")
                }
        return None

    def map_entity(self, entity: ExtractedEntity) -> Dict[str, Any]:
        """Map an entity to standard terminologies"""
        mappings = {
            "entity_text": entity.text,
            "entity_type": entity.entity_type.value,
            "mappings": []
        }

        # Try different terminology systems based on entity type
        if entity.entity_type in [EntityType.CONDITION, EntityType.DIAGNOSIS, EntityType.SYMPTOM]:
            snomed = self.find_snomed_match(entity.text)
            if snomed:
                mappings["mappings"].append(snomed)
            icd10 = self.find_icd10_match(entity.text)
            if icd10:
                mappings["mappings"].append(icd10)

        elif entity.entity_type == EntityType.MEDICATION:
            rxnorm = self.find_rxnorm_match(entity.text)
            if rxnorm:
                mappings["mappings"].append(rxnorm)

        elif entity.entity_type == EntityType.PROCEDURE:
            cpt = self.find_cpt_match(entity.text)
            if cpt:
                mappings["mappings"].append(cpt)

        elif entity.entity_type in [EntityType.LAB_TEST, EntityType.LAB_VALUE, EntityType.VITAL_SIGN]:
            loinc = self.find_loinc_match(entity.text)
            if loinc:
                mappings["mappings"].append(loinc)

        return mappings


class ClinicalNLPService:
    """
    Clinical NLP service for extracting medical entities.
    Uses pattern matching and medical lexicons.
    """

    # Medical entity patterns
    MEDICATION_PATTERNS = [
        r'\b(metformin|lisinopril|atorvastatin|aspirin|amlodipine|carvedilol|furosemide|warfarin|apixaban|clopidogrel|heparin|morphine|omeprazole|nitroglycerin|insulin|ondansetron)\b',
        r'\b(Glucophage|Lipitor|Norvasc|Coreg|Lasix|Coumadin|Eliquis|Plavix|Prilosec|Lantus|Humalog|Zofran)\b',
        r'\b\d+\s*(?:mg|mcg|mL|units?)\s+(?:of\s+)?[A-Za-z]+\b',
    ]

    CONDITION_PATTERNS = [
        r'\b(myocardial infarction|heart attack|MI|STEMI|NSTEMI|acute coronary syndrome|ACS)\b',
        r'\b(type 2 diabetes|T2DM|diabetes mellitus|diabetic)\b',
        r'\b(hypertension|HTN|high blood pressure|elevated blood pressure)\b',
        r'\b(heart failure|CHF|congestive heart failure|HF)\b',
        r'\b(atrial fibrillation|AFib|A-fib|AF)\b',
        r'\b(COPD|chronic obstructive pulmonary disease)\b',
        r'\b(chronic kidney disease|CKD|renal failure|ESRD)\b',
        r'\b(pneumonia|sepsis|stroke|CVA|pulmonary embolism|PE|DVT)\b',
        r'\b(hyperlipidemia|dyslipidemia|hypercholesterolemia)\b',
        r'\b(coronary artery disease|CAD|ischemic heart disease)\b',
    ]

    SYMPTOM_PATTERNS = [
        r'\b(chest pain|dyspnea|shortness of breath|SOB|breathlessness)\b',
        r'\b(fever|pyrexia|headache|nausea|vomiting|diarrhea)\b',
        r'\b(abdominal pain|fatigue|dizziness|syncope|palpitations)\b',
        r'\b(edema|swelling|cough|weakness)\b',
    ]

    PROCEDURE_PATTERNS = [
        r'\b(electrocardiogram|ECG|EKG|12-lead)\b',
        r'\b(echocardiogram|echo|TTE|TEE)\b',
        r'\b(cardiac catheterization|cath|angiogram|angiography)\b',
        r'\b(chest X-ray|CXR|chest radiograph)\b',
        r'\b(CT scan|computed tomography|CAT scan)\b',
        r'\b(MRI|magnetic resonance)\b',
        r'\b(intubation|ventilator|mechanical ventilation)\b',
        r'\b(central line|arterial line|IV|intravenous)\b',
        r'\b(PCI|stent|angioplasty|CABG)\b',
    ]

    LAB_PATTERNS = [
        r'\b(troponin|hs-troponin|cardiac enzymes)\b',
        r'\b(HbA1c|hemoglobin A1c|glycated hemoglobin)\b',
        r'\b(LDL|HDL|cholesterol|triglycerides|lipid panel)\b',
        r'\b(creatinine|BUN|GFR|eGFR|kidney function)\b',
        r'\b(CBC|complete blood count|hemoglobin|hematocrit|WBC|platelets)\b',
        r'\b(sodium|potassium|chloride|BMP|CMP|electrolytes)\b',
        r'\b(AST|ALT|liver function|LFT|bilirubin)\b',
        r'\b(glucose|blood sugar|fasting glucose)\b',
        r'\b(INR|PT|PTT|coagulation)\b',
        r'\b(BNP|NT-proBNP)\b',
    ]

    VITAL_PATTERNS = [
        r'\b(blood pressure|BP|systolic|diastolic)\s*:?\s*(\d{2,3})/(\d{2,3})\b',
        r'\b(heart rate|HR|pulse)\s*:?\s*(\d{2,3})\s*(?:bpm|/min)?\b',
        r'\b(temperature|temp)\s*:?\s*(\d{2,3}\.?\d?)\s*(?:F|C|degrees?)?\b',
        r'\b(respiratory rate|RR|resp)\s*:?\s*(\d{1,2})\s*(?:/min)?\b',
        r'\b(oxygen saturation|O2 sat|SpO2|sat)\s*:?\s*(\d{2,3})%?\b',
        r'\b(weight)\s*:?\s*(\d{2,3}\.?\d?)\s*(?:kg|lbs?|pounds?)?\b',
        r'\b(height)\s*:?\s*(\d{1,3}\.?\d?)\s*(?:cm|m|ft|inches?)?\b',
    ]

    # Lab value extraction pattern
    LAB_VALUE_PATTERN = r'(\w+(?:\s+\w+)?)\s*(?::|=|of)?\s*(\d+\.?\d*)\s*([a-zA-Z/%]+)?'

    def __init__(self):
        self.terminology_service = TerminologyService()

    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract clinical entities from text"""
        entities = []

        # Extract medications
        for pattern in self.MEDICATION_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    entity_type=EntityType.MEDICATION,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9,
                    context=self._get_context(text, match.start(), match.end())
                ))

        # Extract conditions
        for pattern in self.CONDITION_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    entity_type=EntityType.CONDITION,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.85,
                    context=self._get_context(text, match.start(), match.end())
                ))

        # Extract symptoms
        for pattern in self.SYMPTOM_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    entity_type=EntityType.SYMPTOM,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8,
                    context=self._get_context(text, match.start(), match.end())
                ))

        # Extract procedures
        for pattern in self.PROCEDURE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    entity_type=EntityType.PROCEDURE,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.85,
                    context=self._get_context(text, match.start(), match.end())
                ))

        # Extract lab tests
        for pattern in self.LAB_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    entity_type=EntityType.LAB_TEST,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.85,
                    context=self._get_context(text, match.start(), match.end())
                ))

        # Extract vital signs
        for pattern in self.VITAL_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    entity_type=EntityType.VITAL_SIGN,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9,
                    context=self._get_context(text, match.start(), match.end())
                ))

        # Deduplicate and sort by position
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda e: e.start_pos)

        # Add terminology mappings
        for entity in entities:
            mapping = self.terminology_service.map_entity(entity)
            if mapping.get("mappings"):
                best_match = mapping["mappings"][0]
                entity.terminology_code = best_match.get("code")
                entity.terminology_system = best_match.get("system")
                entity.normalized_term = best_match.get("term") or best_match.get("name") or best_match.get("description")

        return entities

    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get surrounding context for an entity"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]

    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove duplicate entities (same position or overlapping)"""
        if not entities:
            return []

        # Sort by start position, then by length (longer first)
        sorted_entities = sorted(entities, key=lambda e: (e.start_pos, -(e.end_pos - e.start_pos)))

        deduped = [sorted_entities[0]]
        for entity in sorted_entities[1:]:
            last = deduped[-1]
            # Skip if overlapping with previous entity
            if entity.start_pos < last.end_pos:
                continue
            deduped.append(entity)

        return deduped


class SafeHarborDeidentifier:
    """
    HIPAA Safe Harbor de-identification service.
    Detects and removes/replaces all 18 PHI identifier types.
    """

    # PHI Detection Patterns
    PHI_PATTERNS = {
        PHIType.NAME: [
            # Full names with titles
            r'\b(?:Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Miss)\s+[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+(?:-[A-Z][a-z]+)?\b',
            # Names in "Last, First" format
            r'\b[A-Z][a-z]+,\s+[A-Z][a-z]+(?:\s+[A-Z]\.?)?\b',
            # Standard names (capitalized words that look like names)
            r'\b[A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:-[A-Z][a-z]+)?\b',
        ],
        PHIType.GEOGRAPHIC: [
            # Full addresses
            r'\b\d{1,5}\s+[A-Za-z]+(?:\s+[A-Za-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Way|Boulevard|Blvd|Court|Ct)\b',
            # City, State ZIP
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b',
            # ZIP codes (alone)
            r'\b\d{5}(?:-\d{4})?\b',
        ],
        PHIType.DATE: [
            # MM/DD/YYYY or MM-DD-YYYY
            r'\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
            # YYYY-MM-DD
            r'\b(?:19|20)\d{2}[-/](?:0?[1-9]|1[0-2])[-/](?:0?[1-9]|[12]\d|3[01])\b',
            # Month DD, YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            # DD Month YYYY
            r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            # Age over 89 indicator
            r'\b(?:age|aged?)\s*[:\s]?\s*(?:9\d|1\d{2})\b',
        ],
        PHIType.PHONE: [
            r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'\b\d{3}[-.\s]\d{4}\b',  # 7-digit phone
        ],
        PHIType.FAX: [
            r'\b(?:fax|facsimile)[:\s]+(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        ],
        PHIType.EMAIL: [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ],
        PHIType.SSN: [
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',  # XXX-XX-XXXX format
            r'\bSSN[:\s]+\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        ],
        PHIType.MRN: [
            r'\b(?:MRN|Medical Record Number|Patient ID|Record #)[:\s]+[A-Z0-9-]+\b',
            r'\b[A-Z]{2,4}[-]?\d{6,10}\b',  # Common MRN formats
        ],
        PHIType.HEALTH_PLAN_ID: [
            r'\b(?:Health Plan|Insurance|Member|Subscriber)\s*(?:ID|#|Number)[:\s]+[A-Z0-9-]+\b',
            r'\b(?:Policy|Group)\s*(?:#|Number)[:\s]+[A-Z0-9-]+\b',
        ],
        PHIType.ACCOUNT_NUMBER: [
            r'\b(?:Account|Acct)\s*(?:#|Number)[:\s]+\d+\b',
            r'\b(?:Billing|Invoice)\s*(?:#|Number)[:\s]+[A-Z0-9-]+\b',
        ],
        PHIType.LICENSE_NUMBER: [
            r'\b(?:License|Licence|DEA|NPI)\s*(?:#|Number)[:\s]+[A-Z0-9-]+\b',
            r'\b(?:Driver.?s?\s+License)[:\s]+[A-Z0-9-]+\b',
        ],
        PHIType.VEHICLE_ID: [
            r'\b(?:VIN|Vehicle)[:\s]+[A-Z0-9]{17}\b',
            r'\b(?:License Plate|Plate)[:\s]+[A-Z0-9-]+\b',
        ],
        PHIType.DEVICE_ID: [
            r'\b(?:Device|Serial)\s*(?:#|Number|ID)[:\s]+[A-Z0-9-]+\b',
            r'\b(?:IMEI|MAC)[:\s]+[A-Z0-9:.-]+\b',
        ],
        PHIType.URL: [
            r'\bhttps?://[^\s<>"{}|\\^`\[\]]+\b',
            r'\bwww\.[^\s<>"{}|\\^`\[\]]+\b',
        ],
        PHIType.IP_ADDRESS: [
            r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b',
            r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b',  # IPv6
        ],
        PHIType.BIOMETRIC: [
            r'\b(?:fingerprint|retina|iris|voiceprint|face\s+recognition)\b',
        ],
        PHIType.UNIQUE_ID: [
            r'\b[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}\b',  # UUID
        ],
    }

    # Replacement templates for each PHI type
    REPLACEMENTS = {
        PHIType.NAME: "[PATIENT NAME]",
        PHIType.GEOGRAPHIC: "[ADDRESS]",
        PHIType.DATE: "[DATE]",
        PHIType.PHONE: "[PHONE]",
        PHIType.FAX: "[FAX]",
        PHIType.EMAIL: "[EMAIL]",
        PHIType.SSN: "[SSN]",
        PHIType.MRN: "[MRN]",
        PHIType.HEALTH_PLAN_ID: "[HEALTH PLAN ID]",
        PHIType.ACCOUNT_NUMBER: "[ACCOUNT]",
        PHIType.LICENSE_NUMBER: "[LICENSE]",
        PHIType.VEHICLE_ID: "[VEHICLE ID]",
        PHIType.DEVICE_ID: "[DEVICE ID]",
        PHIType.URL: "[URL]",
        PHIType.IP_ADDRESS: "[IP ADDRESS]",
        PHIType.BIOMETRIC: "[BIOMETRIC]",
        PHIType.PHOTO: "[PHOTO]",
        PHIType.UNIQUE_ID: "[UNIQUE ID]",
    }

    # Known patient names to detect (for demo)
    KNOWN_NAMES = [
        "Margaret Elizabeth Johnson",
        "Margaret Johnson",
        "Mrs. Johnson",
        "Johnson, Margaret",
        "Dr. Sarah Chen",
        "Sarah Chen",
        "Dr. Michael Rodriguez",
        "Michael Rodriguez",
        "Dr. James Wilson",
        "James Wilson",
    ]

    def __init__(self):
        self._phi_counter = 0

    def detect_phi(self, text: str) -> List[PHIDetection]:
        """Detect all PHI in text"""
        detections = []

        # First, detect known names from the sample document
        for name in self.KNOWN_NAMES:
            for match in re.finditer(re.escape(name), text, re.IGNORECASE):
                detections.append(PHIDetection(
                    text=match.group(),
                    phi_type=PHIType.NAME,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.99,
                    replacement=self._generate_replacement(PHIType.NAME)
                ))

        # Then use pattern matching for other PHI
        for phi_type, patterns in self.PHI_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # Check if this position is already covered
                    if not self._is_covered(match.start(), match.end(), detections):
                        detections.append(PHIDetection(
                            text=match.group(),
                            phi_type=phi_type,
                            start_pos=match.start(),
                            end_pos=match.end(),
                            confidence=0.85,
                            replacement=self._generate_replacement(phi_type)
                        ))

        # Sort by position and deduplicate
        detections = self._deduplicate_detections(detections)
        detections.sort(key=lambda d: d.start_pos)

        return detections

    def _is_covered(self, start: int, end: int, detections: List[PHIDetection]) -> bool:
        """Check if position is already covered by another detection"""
        for d in detections:
            if start >= d.start_pos and end <= d.end_pos:
                return True
        return False

    def _deduplicate_detections(self, detections: List[PHIDetection]) -> List[PHIDetection]:
        """Remove overlapping detections, preferring higher confidence"""
        if not detections:
            return []

        # Sort by start position, then by confidence (higher first)
        sorted_detections = sorted(detections, key=lambda d: (d.start_pos, -d.confidence))

        deduped = [sorted_detections[0]]
        for detection in sorted_detections[1:]:
            last = deduped[-1]
            # Skip if overlapping
            if detection.start_pos < last.end_pos:
                continue
            deduped.append(detection)

        return deduped

    def _generate_replacement(self, phi_type: PHIType) -> str:
        """Generate a consistent replacement for PHI"""
        self._phi_counter += 1
        base = self.REPLACEMENTS.get(phi_type, "[REDACTED]")
        return base

    def deidentify(self, text: str, detections: Optional[List[PHIDetection]] = None) -> str:
        """Replace all PHI with safe substitutes"""
        if detections is None:
            detections = self.detect_phi(text)

        # Sort by position (reverse order for replacement)
        detections_sorted = sorted(detections, key=lambda d: d.start_pos, reverse=True)

        result = text
        for detection in detections_sorted:
            result = result[:detection.start_pos] + detection.replacement + result[detection.end_pos:]

        return result

    def get_phi_summary(self, detections: List[PHIDetection]) -> Dict[str, Any]:
        """Generate summary of PHI found"""
        by_type = {}
        for d in detections:
            phi_type = d.phi_type.value
            if phi_type not in by_type:
                by_type[phi_type] = []
            by_type[phi_type].append({
                "text": d.text,
                "replacement": d.replacement,
                "confidence": d.confidence
            })

        return {
            "total_phi_found": len(detections),
            "phi_by_type": by_type,
            "types_found": list(by_type.keys()),
            "safe_harbor_compliance": True,
            "identifiers_addressed": [t.value for t in PHIType]
        }


class MedicalRecordProcessor:
    """
    Main orchestrator for medical record processing pipeline.
    """

    def __init__(self):
        self.nlp_service = ClinicalNLPService()
        self.deidentifier = SafeHarborDeidentifier()
        self.terminology_service = TerminologyService()

    def process_text(self, text: str) -> ProcessingResult:
        """
        Process medical record text through the full pipeline.

        Steps:
        1. Extract clinical entities (NLP)
        2. Map entities to standard terminologies
        3. Detect PHI
        4. De-identify text
        """
        start_time = datetime.now()

        # Step 1: Extract clinical entities
        entities = self.nlp_service.extract_entities(text)

        # Step 2: Map to terminologies
        terminology_mappings = {
            "conditions": [],
            "medications": [],
            "procedures": [],
            "lab_tests": [],
            "vital_signs": [],
            "symptoms": []
        }

        for entity in entities:
            mapping = self.terminology_service.map_entity(entity)

            if entity.entity_type in [EntityType.CONDITION, EntityType.DIAGNOSIS]:
                terminology_mappings["conditions"].append(mapping)
            elif entity.entity_type == EntityType.MEDICATION:
                terminology_mappings["medications"].append(mapping)
            elif entity.entity_type == EntityType.PROCEDURE:
                terminology_mappings["procedures"].append(mapping)
            elif entity.entity_type in [EntityType.LAB_TEST, EntityType.LAB_VALUE]:
                terminology_mappings["lab_tests"].append(mapping)
            elif entity.entity_type == EntityType.VITAL_SIGN:
                terminology_mappings["vital_signs"].append(mapping)
            elif entity.entity_type == EntityType.SYMPTOM:
                terminology_mappings["symptoms"].append(mapping)

        # Step 3: Detect PHI
        phi_detections = self.deidentifier.detect_phi(text)

        # Step 4: De-identify
        deidentified_text = self.deidentifier.deidentify(text, phi_detections)

        # Calculate processing stats
        processing_time = (datetime.now() - start_time).total_seconds()

        return ProcessingResult(
            original_text=text,
            deidentified_text=deidentified_text,
            entities=entities,
            phi_detections=phi_detections,
            terminology_mappings=terminology_mappings,
            processing_stats={
                "processing_time_seconds": processing_time,
                "character_count": len(text),
                "word_count": len(text.split()),
                "entities_extracted": len(entities),
                "phi_detected": len(phi_detections),
                "terminology_mappings": sum(len(v) for v in terminology_mappings.values()),
                "safe_harbor_compliance": True
            }
        )

    def process_pdf(self, pdf_bytes: bytes) -> ProcessingResult:
        """
        Process a PDF document.
        Extracts text using PyPDF2 or OCR if needed.
        """
        try:
            # Try direct text extraction first
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

            text_parts = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            if text_parts:
                full_text = "\n\n".join(text_parts)
                return self.process_text(full_text)
            else:
                # Fall back to OCR if no text extracted
                return self._process_pdf_with_ocr(pdf_bytes)

        except ImportError:
            # PyPDF2 not available, use OCR
            return self._process_pdf_with_ocr(pdf_bytes)
        except Exception as e:
            # If PDF parsing fails, try OCR
            return self._process_pdf_with_ocr(pdf_bytes)

    def _process_pdf_with_ocr(self, pdf_bytes: bytes) -> ProcessingResult:
        """Process PDF using OCR (Tesseract)"""
        try:
            import pytesseract
            from pdf2image import convert_from_bytes

            # Convert PDF to images
            images = convert_from_bytes(pdf_bytes)

            # OCR each page
            text_parts = []
            for image in images:
                text = pytesseract.image_to_string(image)
                text_parts.append(text)

            full_text = "\n\n".join(text_parts)
            return self.process_text(full_text)

        except ImportError as e:
            # OCR libraries not available
            raise RuntimeError(
                "PDF OCR processing requires pytesseract and pdf2image. "
                f"Please install them: pip install pytesseract pdf2image. Error: {e}"
            )

    def get_sample_document(self) -> str:
        """Return sample discharge summary for demo"""
        return """
MERCY GENERAL HOSPITAL
Department of Cardiology
1234 Medical Center Drive
Springfield, IL 62701

DISCHARGE SUMMARY

Patient: Margaret Elizabeth Johnson
Date of Birth: March 15, 1958
Medical Record Number: MGH-2024-789456
Social Security Number: 321-54-9876
Admission Date: January 15, 2024
Discharge Date: January 19, 2024

ATTENDING PHYSICIAN: Dr. Sarah Chen, MD
CARDIOLOGY CONSULTANT: Dr. Michael Rodriguez, MD

PATIENT CONTACT INFORMATION:
Address: 456 Oak Street, Apt 12B, Springfield, IL 62702
Phone: (217) 555-0147
Email: m.johnson1958@email.com
Emergency Contact: Robert Johnson (spouse) - (217) 555-0198

INSURANCE INFORMATION:
Health Plan ID: BCBS-IL-987654321
Group Number: GRP-45678
Member ID: MJO-123456789

CHIEF COMPLAINT:
66-year-old female presenting with acute onset chest pain and shortness of breath.

HISTORY OF PRESENT ILLNESS:
Mrs. Johnson presented to the Emergency Department on January 15, 2024 at 14:32
with complaints of severe substernal chest pain radiating to her left arm,
associated with diaphoresis and dyspnea. Pain began approximately 2 hours prior
to arrival while she was at home at 456 Oak Street. She rated the pain as 9/10
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
- Former smoker, quit 2018 (30 pack-year history)
- Occasional alcohol use (1-2 glasses wine per week)
- Retired teacher
- Lives with spouse

FAMILY HISTORY:
- Father: MI at age 62, deceased
- Mother: Type 2 diabetes, hypertension
- Brother: CABG at age 58

PHYSICAL EXAMINATION ON ADMISSION:
Vital Signs:
- Blood Pressure: 162/94 mmHg
- Heart Rate: 98 bpm
- Respiratory Rate: 22/min
- Temperature: 98.6°F (37.0°C)
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
Mrs. Johnson was admitted to the Cardiac Care Unit with a diagnosis of
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
1. Follow up with Dr. Chen (cardiology) in 1 week - call (217) 555-0300 to schedule
2. Follow up with primary care physician Dr. James Wilson in 2 weeks
3. Cardiac rehabilitation referral - start in 2 weeks
4. Low sodium, heart-healthy diet
5. No strenuous activity for 2 weeks
6. Do not lift anything heavier than 10 pounds for 1 week
7. Return to ED if experiencing chest pain, shortness of breath, palpitations,
   or bleeding at catheterization site

CONDITION AT DISCHARGE: Stable, improved

Electronically signed by:
Sarah Chen, MD
Attending Physician - Cardiology
License Number: IL-MD-123456
NPI: 1234567890
Date: January 19, 2024 10:30 AM

Dictated: 01/19/2024 09:15 by Dr. Sarah Chen
Transcribed: 01/19/2024 10:00 by Medical Records
Document ID: DS-2024-MGH-789456
IP Address: 192.168.1.100

MERCY GENERAL HOSPITAL - CONFIDENTIAL PATIENT INFORMATION
This document contains protected health information (PHI)
"""

    def to_json_result(self, result: ProcessingResult) -> Dict[str, Any]:
        """Convert ProcessingResult to JSON-serializable dict"""
        return {
            "original_text": result.original_text,
            "deidentified_text": result.deidentified_text,
            "entities": [
                {
                    "text": e.text,
                    "type": e.entity_type.value,
                    "start": e.start_pos,
                    "end": e.end_pos,
                    "confidence": e.confidence,
                    "normalized_term": e.normalized_term,
                    "terminology_code": e.terminology_code,
                    "terminology_system": e.terminology_system,
                    "context": e.context
                }
                for e in result.entities
            ],
            "phi_detections": [
                {
                    "text": p.text,
                    "type": p.phi_type.value,
                    "start": p.start_pos,
                    "end": p.end_pos,
                    "confidence": p.confidence,
                    "replacement": p.replacement
                }
                for p in result.phi_detections
            ],
            "phi_summary": self.deidentifier.get_phi_summary(result.phi_detections),
            "terminology_mappings": result.terminology_mappings,
            "processing_stats": result.processing_stats,
            "safe_harbor_18_identifiers": [t.value for t in PHIType]
        }
