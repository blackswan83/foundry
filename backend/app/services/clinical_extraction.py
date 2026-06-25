"""
Clinical Text Extraction & SNOMED Annotation Service (Elembic)

This is the Elembic named-entity-recognition and entity-linking (NER+L) layer.
It takes *unstructured* clinical / molecular-pathology free text and produces:

  1. Recognized entity spans, color-coded by type
  2. Entity links to the correct vocabulary:
        - SNOMED CT for clinical findings, tumor morphology, procedures and
          anatomical sites (the clinical layer)
        - HGNC for genes, HGVS for variants, ClinVar for clinical significance,
          and LOINC for molecular assays (the molecular / genomic layer)
  3. Context flags per entity: negation, temporality (historical vs current),
     experiencer (patient vs family)
  4. Confidence scores with a caller-adjustable threshold
  5. A full "operations performed" audit trail

Approach & honesty note (for the build team, surfaced in the UI):
  This demo mirrors the real Elembic stack (MedCAT for NER+L, a MetaCAT-style
  meta-annotation layer for negation / temporality / experiencer) but runs a
  curated, deterministic dictionary+rule engine so the demo is reproducible
  offline. No live model weights are loaded. Every concept id below is
  ILLUSTRATIVE and must be validated against a live terminology server before
  the call — do not present these as production-validated codes.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# --------------------------------------------------------------------------- #
#  Entity types (drive the inline color-coding in the UI)
# --------------------------------------------------------------------------- #

ENTITY_TYPES = {
    "condition": {"label": "Condition / Disorder", "layer": "clinical", "color": "#c0392b"},
    "morphology": {"label": "Finding / Morphology", "layer": "clinical", "color": "#d35400"},
    "procedure": {"label": "Procedure", "layer": "clinical", "color": "#27ae60"},
    "medication": {"label": "Medication", "layer": "clinical", "color": "#2980b9"},
    "lab": {"label": "Lab / Assay", "layer": "clinical", "color": "#8e44ad"},
    "anatomical_site": {"label": "Anatomical Site", "layer": "clinical", "color": "#16a085"},
    "gene": {"label": "Gene", "layer": "molecular", "color": "#b7950b"},
    "variant": {"label": "Variant", "layer": "molecular", "color": "#a04000"},
    "biomarker": {"label": "Biomarker", "layer": "molecular", "color": "#6c3483"},
}


@dataclass
class Concept:
    """A single linkable concept in the curated knowledge base."""
    triggers: List[str]                 # surface forms to match (case-insensitive)
    entity_type: str                    # key in ENTITY_TYPES
    vocabulary: str                     # SNOMED CT | HGNC | HGVS | ClinVar | LOINC
    code: str                           # concept id / code (illustrative)
    preferred_term: str
    semantic_tag: str = ""              # e.g. disorder, body structure, gene
    confidence: float = 0.90            # base linking confidence
    note: str = ""                      # optional extra detail (e.g. ClinVar significance)


@dataclass
class ExtractedEntity:
    """A recognized + linked entity, with context flags."""
    text: str
    entity_type: str
    start: int
    end: int
    vocabulary: str
    code: str
    preferred_term: str
    semantic_tag: str
    confidence: float
    negated: bool
    historical: bool
    subject: str                        # "patient" | "family"
    sentence: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "entity_type": self.entity_type,
            "entity_type_label": ENTITY_TYPES.get(self.entity_type, {}).get("label", self.entity_type),
            "layer": ENTITY_TYPES.get(self.entity_type, {}).get("layer", "clinical"),
            "color": ENTITY_TYPES.get(self.entity_type, {}).get("color", "#555"),
            "start": self.start,
            "end": self.end,
            "vocabulary": self.vocabulary,
            "code": self.code,
            "concept": self.preferred_term,
            "semantic_tag": self.semantic_tag,
            "confidence": round(self.confidence, 2),
            "negated": self.negated,
            "historical": self.historical,
            "subject": self.subject,
            "context": self.sentence.strip(),
            "note": self.note,
        }


# --------------------------------------------------------------------------- #
#  Curated, illustrative knowledge base
#  (SNOMED CT clinical layer + HGNC/HGVS/ClinVar/LOINC molecular layer)
# --------------------------------------------------------------------------- #

KNOWLEDGE_BASE: List[Concept] = [
    # ---- Conditions / disorders (SNOMED CT) ----
    Concept(["non-st elevation myocardial infarction", "nstemi", "non-stemi"], "condition", "SNOMED CT", "401303003", "Acute non-ST segment elevation myocardial infarction", "disorder", 0.96),
    Concept(["myocardial infarction", "heart attack", "stemi"], "condition", "SNOMED CT", "22298006", "Myocardial infarction", "disorder", 0.94),
    Concept(["acute coronary syndrome", "acs"], "condition", "SNOMED CT", "394659003", "Acute coronary syndrome", "disorder", 0.92),
    Concept(["coronary artery disease", "coronary artery disease (cad)", "cad", "ischemic heart disease"], "condition", "SNOMED CT", "53741008", "Coronary arteriosclerosis", "disorder", 0.91),
    Concept(["type 2 diabetes mellitus", "type 2 diabetes", "t2dm", "diabetes mellitus"], "condition", "SNOMED CT", "44054006", "Type 2 diabetes mellitus", "disorder", 0.95),
    Concept(["essential hypertension", "hypertension", "htn"], "condition", "SNOMED CT", "59621000", "Essential hypertension", "disorder", 0.93),
    Concept(["hyperlipidemia", "dyslipidemia", "hypercholesterolemia"], "condition", "SNOMED CT", "55822004", "Hyperlipidemia", "disorder", 0.9),
    Concept(["heart failure", "congestive heart failure", "chf"], "condition", "SNOMED CT", "84114007", "Heart failure", "disorder", 0.92),
    Concept(["acute kidney injury", "aki", "acute renal failure"], "condition", "SNOMED CT", "14669001", "Acute kidney injury", "disorder", 0.9),
    Concept(["acute respiratory failure", "respiratory failure"], "condition", "SNOMED CT", "65710008", "Acute respiratory failure", "disorder", 0.89),
    Concept(["sepsis", "septic shock"], "condition", "SNOMED CT", "91302008", "Sepsis", "disorder", 0.9),
    Concept(["community-acquired pneumonia", "pneumonia"], "condition", "SNOMED CT", "233604007", "Pneumonia", "disorder", 0.9),
    Concept(["non-small cell lung cancer", "non-small-cell lung carcinoma", "nsclc"], "condition", "SNOMED CT", "254637007", "Non-small cell lung cancer", "disorder", 0.95),
    Concept(["adenocarcinoma of the lung", "adenocarcinoma of lung", "lung adenocarcinoma", "pulmonary adenocarcinoma"], "condition", "SNOMED CT", "254626006", "Adenocarcinoma of lung", "disorder", 0.96),
    Concept(["malignant neoplasm", "malignancy", "malignant tumor"], "condition", "SNOMED CT", "363346000", "Malignant neoplastic disease", "disorder", 0.86),

    # ---- Findings / morphology (SNOMED CT) ----
    Concept(["adenocarcinoma"], "morphology", "SNOMED CT", "35917007", "Adenocarcinoma", "morphologic abnormality", 0.9),
    Concept(["poorly differentiated", "poor differentiation"], "morphology", "SNOMED CT", "63283001", "Poorly differentiated", "qualifier value", 0.82),
    Concept(["lymphovascular invasion"], "morphology", "SNOMED CT", "371512006", "Presence of lymphovascular invasion", "finding", 0.84),
    Concept(["st-segment depression", "st segment depression", "st depression"], "morphology", "SNOMED CT", "164931005", "ST segment depression", "finding", 0.85),
    Concept(["hypokinesis", "wall hypokinesis", "anterior hypokinesis"], "morphology", "SNOMED CT", "53533004", "Hypokinesia of cardiac wall", "finding", 0.8),
    Concept(["pulmonary congestion", "vascular congestion"], "morphology", "SNOMED CT", "196911008", "Pulmonary congestion", "finding", 0.82),
    Concept(["chest pain"], "morphology", "SNOMED CT", "29857009", "Chest pain", "finding", 0.88),
    Concept(["shortness of breath", "dyspnea", "breathlessness"], "morphology", "SNOMED CT", "267036007", "Dyspnea", "finding", 0.88),

    # ---- Procedures (SNOMED CT) ----
    Concept(["percutaneous coronary intervention", "pci"], "procedure", "SNOMED CT", "415070008", "Percutaneous coronary intervention", "procedure", 0.93),
    Concept(["cardiac catheterization", "coronary angiography", "cardiac cath"], "procedure", "SNOMED CT", "41976001", "Cardiac catheterization", "procedure", 0.91),
    Concept(["echocardiogram", "echocardiography", "transthoracic echocardiogram", "tte"], "procedure", "SNOMED CT", "40701008", "Echocardiography", "procedure", 0.91),
    Concept(["electrocardiogram", "ecg", "ekg", "12-lead ecg"], "procedure", "SNOMED CT", "29303009", "Electrocardiographic procedure", "procedure", 0.92),
    Concept(["mechanical ventilation", "mechanical ventilatory support"], "procedure", "SNOMED CT", "40617009", "Artificial respiration", "procedure", 0.86),
    Concept(["drug-eluting stent", "coronary stent placement", "stent placement"], "procedure", "SNOMED CT", "36969009", "Placement of stent in coronary artery", "procedure", 0.85),
    Concept(["ct-guided core needle biopsy", "core needle biopsy", "needle biopsy", "transthoracic biopsy"], "procedure", "SNOMED CT", "67800003", "Core needle biopsy", "procedure", 0.88),
    Concept(["biopsy of lung", "lung biopsy"], "procedure", "SNOMED CT", "173978000", "Biopsy of lung", "procedure", 0.87),
    Concept(["immunohistochemistry", "ihc"], "procedure", "SNOMED CT", "250564007", "Immunohistochemistry technique", "procedure", 0.84),
    Concept(["next-generation sequencing", "ngs", "next generation sequencing"], "procedure", "SNOMED CT", "117040002", "Nucleic acid sequencing", "procedure", 0.82),

    # ---- Anatomical sites (SNOMED CT) ----
    Concept(["left upper lobe of the lung", "left upper lobe", "lul"], "anatomical_site", "SNOMED CT", "45653009", "Structure of left upper lobe of lung", "body structure", 0.9),
    Concept(["lung parenchyma", "lung"], "anatomical_site", "SNOMED CT", "39607008", "Lung structure", "body structure", 0.85),
    Concept(["pleura", "pleural surface"], "anatomical_site", "SNOMED CT", "3120008", "Pleural structure", "body structure", 0.82),
    Concept(["mediastinal lymph node", "mediastinal lymph nodes"], "anatomical_site", "SNOMED CT", "127157005", "Mediastinal lymph node structure", "body structure", 0.83),
    Concept(["left anterior descending", "lad coronary artery", "lad artery"], "anatomical_site", "SNOMED CT", "59820001", "Structure of left anterior descending coronary artery", "body structure", 0.84),

    # ---- Medications (RxNorm) ----
    Concept(["aspirin"], "medication", "RxNorm", "1191", "Aspirin", "substance", 0.92),
    Concept(["clopidogrel", "plavix"], "medication", "RxNorm", "32968", "Clopidogrel", "substance", 0.92),
    Concept(["atorvastatin", "lipitor"], "medication", "RxNorm", "83367", "Atorvastatin", "substance", 0.92),
    Concept(["metoprolol", "toprol"], "medication", "RxNorm", "6918", "Metoprolol", "substance", 0.9),
    Concept(["lisinopril"], "medication", "RxNorm", "29046", "Lisinopril", "substance", 0.9),
    Concept(["metformin"], "medication", "RxNorm", "6809", "Metformin", "substance", 0.9),
    Concept(["heparin"], "medication", "RxNorm", "5224", "Heparin", "substance", 0.88),
    Concept(["nitroglycerin"], "medication", "RxNorm", "4917", "Nitroglycerin", "substance", 0.87),
    Concept(["osimertinib", "tagrisso"], "medication", "RxNorm", "1721560", "Osimertinib", "substance", 0.9),
    Concept(["pembrolizumab", "keytruda"], "medication", "RxNorm", "1547545", "Pembrolizumab", "substance", 0.9),

    # ---- Labs / assays (LOINC) ----
    Concept(["troponin i", "troponin", "hs-troponin"], "lab", "LOINC", "10839-9", "Troponin I, cardiac [Mass/volume]", "lab", 0.9),
    Concept(["hba1c", "hemoglobin a1c", "glycated hemoglobin"], "lab", "LOINC", "4548-4", "Hemoglobin A1c/Hemoglobin.total", "lab", 0.9),
    Concept(["bnp", "b-type natriuretic peptide"], "lab", "LOINC", "30934-4", "Natriuretic peptide B [Mass/volume]", "lab", 0.86),
    Concept(["ldl cholesterol", "ldl"], "lab", "LOINC", "13457-7", "LDL cholesterol (calculated)", "lab", 0.86),
    Concept(["creatinine"], "lab", "LOINC", "2160-0", "Creatinine [Mass/volume] in Serum or Plasma", "lab", 0.88),
    Concept(["egfr mutation analysis", "egfr mutation testing", "egfr gene mutation analysis"], "lab", "LOINC", "21665-5", "EGFR gene mutations found [Identifier]", "lab", 0.9),
    Concept(["pd-l1 immunohistochemistry", "pd-l1 ihc", "pd-l1 assay"], "lab", "LOINC", "83346-9", "PD-L1 [Presence] by Immune stain", "lab", 0.86),

    # ---- Genes (HGNC) ----
    Concept(["egfr", "epidermal growth factor receptor"], "gene", "HGNC", "HGNC:3236", "EGFR", "gene", 0.95, note="Epidermal growth factor receptor; chr 7p11.2"),
    Concept(["alk"], "gene", "HGNC", "HGNC:427", "ALK", "gene", 0.9, note="ALK receptor tyrosine kinase; chr 2p23.2"),
    Concept(["kras"], "gene", "HGNC", "HGNC:6407", "KRAS", "gene", 0.9, note="KRAS proto-oncogene; chr 12p12.1"),
    Concept(["ros1"], "gene", "HGNC", "HGNC:10261", "ROS1", "gene", 0.88, note="ROS proto-oncogene 1; chr 6q22.1"),
    Concept(["pd-l1", "cd274", "programmed death-ligand 1"], "gene", "HGNC", "HGNC:17635", "CD274", "gene", 0.88, note="CD274 / PD-L1; chr 9p24.1"),
    Concept(["braf"], "gene", "HGNC", "HGNC:1097", "BRAF", "gene", 0.88, note="B-Raf proto-oncogene; chr 7q34"),

    # ---- Variants (HGVS) + clinical significance (ClinVar) ----
    Concept(["exon 19 deletion", "exon 19 in-frame deletion", "ex19del", "e746_a750del", "p.glu746_ala750del"], "variant", "HGVS", "p.Glu746_Ala750del", "EGFR exon 19 in-frame deletion (c.2235_2249del)", "variant", 0.92, note="ClinVar: Pathogenic; EGFR-TKI sensitizing"),
    Concept(["l858r", "p.leu858arg", "exon 21 l858r"], "variant", "HGVS", "p.Leu858Arg", "EGFR p.Leu858Arg (c.2573T>G)", "variant", 0.9, note="ClinVar: Pathogenic; EGFR-TKI sensitizing"),
    Concept(["t790m", "p.thr790met"], "variant", "HGVS", "p.Thr790Met", "EGFR p.Thr790Met (c.2369C>T)", "variant", 0.9, note="ClinVar: Pathogenic; EGFR-TKI resistance"),
    Concept(["g12c", "p.gly12cys", "kras g12c"], "variant", "HGVS", "p.Gly12Cys", "KRAS p.Gly12Cys (c.34G>T)", "variant", 0.9, note="ClinVar: Pathogenic; KRAS G12C-inhibitor target"),

    # ---- Biomarkers (molecular result expressions) ----
    Concept(["pd-l1 tps", "tumor proportion score", "pd-l1 expression"], "biomarker", "LOINC", "83346-9", "PD-L1 tumor proportion score", "biomarker", 0.85, note="Reported as Tumor Proportion Score (TPS)"),
    Concept(["egfr gene mutation positive", "egfr-mutant", "egfr mutated", "egfr positive"], "biomarker", "SNOMED CT", "405923000", "Epidermal growth factor receptor gene mutation positive", "finding", 0.85, note="Illustrative SNOMED finding for the EGFR-positive result"),
]


# Negation / temporality / experiencer cue lexicons
NEGATION_CUES = [
    "no evidence of", "no evidence", "negative for", "no ", "without",
    "denies", "denied", "absence of", "absent", "ruled out", "rule out",
    "not detected", "not identified", "no significant", "free of", "unremarkable for",
]
NEGATION_POST_CUES = [
    "negative", "not detected", "not identified", "not required", "no mutation",
    "no rearrangement", "no fusion", "no evidence", "absent", "wild-type", "wild type",
]

HISTORICAL_CUES = [
    "history of", "h/o", "hx of", "past medical history", "pmh", "previously",
    "previous", "prior", "status post", "s/p", "in 20", "years ago", "year ago",
    "diagnosed in", "diagnosed 20", "old ", "remote", "resolved",
]

FAMILY_CUES = [
    "family history", "fh:", "father", "mother", "brother", "sister", "sibling",
    "parent", "maternal", "paternal", "grandfather", "grandmother", "son", "daughter",
]


class ClinicalExtractionService:
    """Elembic NER + entity-linking + context-detection engine (curated demo)."""

    def __init__(self) -> None:
        # Pre-compile a regex per trigger, longest first so multi-word phrases win.
        self._compiled: List[Tuple[re.Pattern, Concept, str]] = []
        for concept in KNOWLEDGE_BASE:
            for trigger in sorted(concept.triggers, key=len, reverse=True):
                pattern = re.compile(r"(?<![A-Za-z0-9])" + re.escape(trigger) + r"(?![A-Za-z0-9])", re.IGNORECASE)
                self._compiled.append((pattern, concept, trigger))

    # ----- segmentation -------------------------------------------------- #

    @staticmethod
    def _split_sentences(text: str) -> List[Tuple[int, int, str]]:
        """Return contiguous (start, end, sentence_text) tuples. Splits on
        sentence-ending punctuation and on blank lines (section/paragraph
        breaks) but NOT on single newlines, because clinical notes wrap
        sentences mid-line — keeping wrapped lines together preserves negation
        and temporality context (e.g. 'no evidence of\\npulmonary congestion')."""
        spans = []
        pos = 0
        for match in re.finditer(r"[.!?]+(?=\s|$)|\n\s*\n", text):
            end = match.end()
            seg = text[pos:end]
            if seg.strip():
                spans.append((pos, end, seg))
            pos = end
        if pos < len(text) and text[pos:].strip():
            spans.append((pos, len(text), text[pos:]))
        return spans

    @staticmethod
    def _detect_sections(text: str) -> List[Tuple[int, str]]:
        """Return (offset, SECTION_NAME) for UPPERCASE header lines so that
        section context (e.g. PAST MEDICAL HISTORY, FAMILY HISTORY) can be used
        for temporality / experiencer detection."""
        sections = []
        for match in re.finditer(r"(?m)^\s*([A-Z][A-Z /&-]{3,}):", text):
            sections.append((match.start(), match.group(1).strip()))
        return sections

    # ----- public API ---------------------------------------------------- #

    def extract(self, text: str, threshold: float = 0.5) -> Dict[str, Any]:
        started = datetime.now()

        sentences = self._split_sentences(text)
        sections = self._detect_sections(text)

        # 1) NER: collect all candidate spans
        candidates: List[ExtractedEntity] = []
        for pattern, concept, trigger in self._compiled:
            for m in pattern.finditer(text):
                exact = m.group().lower() == concept.preferred_term.lower()
                conf = concept.confidence + (0.02 if exact else 0.0)
                conf = max(0.0, min(conf, 0.99))
                candidates.append(ExtractedEntity(
                    text=m.group(),
                    entity_type=concept.entity_type,
                    start=m.start(),
                    end=m.end(),
                    vocabulary=concept.vocabulary,
                    code=concept.code,
                    preferred_term=concept.preferred_term,
                    semantic_tag=concept.semantic_tag,
                    confidence=conf,
                    negated=False,
                    historical=False,
                    subject="patient",
                    sentence="",
                    note=concept.note,
                ))

        total_candidates = len(candidates)

        # 2) Resolve overlaps: longest span wins, then highest confidence
        resolved = self._resolve_overlaps(candidates)
        linked_count = len(resolved)

        # 3) Context detection (negation / temporality / experiencer)
        for ent in resolved:
            s_start, _s_end, sent = self._sentence_for(ent.start, sentences)
            ent.sentence = sent
            section = self._section_for(ent.start, sections)
            self._apply_context(ent, ent.start - s_start, sent, section)

        # 4) Confidence threshold
        kept = [e for e in resolved if e.confidence >= threshold]
        kept.sort(key=lambda e: e.start)
        dropped = linked_count - len(kept)

        elapsed_ms = (datetime.now() - started).total_seconds() * 1000

        operations = self._build_operations(
            text=text,
            sentences=sentences,
            sections=sections,
            total_candidates=total_candidates,
            linked=linked_count,
            kept=kept,
            dropped=dropped,
            threshold=threshold,
            elapsed_ms=elapsed_ms,
        )

        return {
            "entities": [e.to_dict() for e in kept],
            "operations": operations,
            "entity_types": ENTITY_TYPES,
            "stats": {
                "characters": len(text),
                "words": len(text.split()),
                "sentences": len(sentences),
                "sections": len(sections),
                "candidate_spans": total_candidates,
                "entities_linked": linked_count,
                "entities_passed_threshold": len(kept),
                "entities_below_threshold": dropped,
                "negated_entities": sum(1 for e in kept if e.negated),
                "historical_entities": sum(1 for e in kept if e.historical),
                "family_entities": sum(1 for e in kept if e.subject == "family"),
                "clinical_layer": sum(1 for e in kept if ENTITY_TYPES[e.entity_type]["layer"] == "clinical"),
                "molecular_layer": sum(1 for e in kept if ENTITY_TYPES[e.entity_type]["layer"] == "molecular"),
                "threshold": threshold,
                "processing_ms": round(elapsed_ms, 1),
            },
            "vocabularies_used": sorted({e.vocabulary for e in kept}),
            "disclaimer": (
                "Synthetic input. Codes are ILLUSTRATIVE (MedCAT/MetaCAT-style demo) "
                "and must be validated against a live terminology server before use."
            ),
        }

    # ----- helpers ------------------------------------------------------- #

    @staticmethod
    def _resolve_overlaps(cands: List[ExtractedEntity]) -> List[ExtractedEntity]:
        # Longest span first, then highest confidence; greedily keep non-overlapping.
        cands_sorted = sorted(cands, key=lambda e: (e.start, -(e.end - e.start), -e.confidence))
        kept: List[ExtractedEntity] = []
        occupied: List[Tuple[int, int]] = []
        for ent in cands_sorted:
            if any(ent.start < o_end and ent.end > o_start for o_start, o_end in occupied):
                continue
            kept.append(ent)
            occupied.append((ent.start, ent.end))
        kept.sort(key=lambda e: e.start)
        return kept

    @staticmethod
    def _sentence_for(pos: int, sentences: List[Tuple[int, int, str]]) -> Tuple[int, int, str]:
        for s, e, txt in sentences:
            if s <= pos < e:
                return s, e, txt
        return pos, pos, ""

    @staticmethod
    def _section_for(pos: int, sections: List[Tuple[int, str]]) -> str:
        current = ""
        for offset, name in sections:
            if offset <= pos:
                current = name
            else:
                break
        return current

    def _apply_context(self, ent: ExtractedEntity, rel: int, sentence: str, section: str) -> None:
        lower_sent = sentence.replace("\n", " ").lower()
        span_len = ent.end - ent.start
        # windows immediately before / after the entity within its sentence
        # (newlines normalised to spaces so wrapped lines read continuously)
        pre_window = sentence[max(0, rel - 45): rel].replace("\n", " ").lower()
        post_window = sentence[rel + span_len: rel + span_len + 30].replace("\n", " ").lower()

        # Negation (pre cues like "no evidence of", or post cues like "X negative")
        if any(cue in pre_window for cue in NEGATION_CUES) or any(cue in post_window for cue in NEGATION_POST_CUES):
            ent.negated = True

        # Experiencer (family vs patient) — evaluate first so we don't also tag
        # family-history items as the patient's own past history.
        section_l = section.lower()
        is_family = "family history" in section_l or any(cue in lower_sent for cue in FAMILY_CUES)

        # Temporality (section- or cue-driven), patient timeline only.
        # "History of present illness" describes the CURRENT episode, so it must
        # not be read as historical even though it contains the word "history".
        present_illness = "present illness" in section_l or "present illness" in lower_sent
        if not is_family and not present_illness:
            if "past" in section_l or "pmh" in section_l:
                ent.historical = True
            if any(cue in lower_sent for cue in HISTORICAL_CUES):
                ent.historical = True

        # Experiencer (family vs patient)
        if is_family:
            # genes/variants/biomarkers are reported on the patient's tumor even in
            # mixed sentences, so only flag clinical findings as family-attributed
            if ENTITY_TYPES[ent.entity_type]["layer"] == "clinical":
                ent.subject = "family"

    def _build_operations(self, *, text, sentences, sections, total_candidates,
                          linked, kept, dropped, threshold, elapsed_ms) -> List[Dict[str, Any]]:
        """The 'operations performed' audit trail Petros asked for — explicit
        inputs, transformations and outputs, no black boxes."""
        return [
            {"step": 1, "operation": "Document parsed", "detail": f"{len(text)} characters, {len(text.split())} tokens ingested", "count": len(text)},
            {"step": 2, "operation": "Segmentation", "detail": f"Split into {len(sentences)} sentences across {len(sections)} sections", "count": len(sentences)},
            {"step": 3, "operation": "Named-entity recognition (MedCAT-style)", "detail": f"{total_candidates} candidate spans detected", "count": total_candidates},
            {"step": 4, "operation": "Overlap resolution", "detail": f"{linked} spans retained after longest-match resolution", "count": linked},
            {"step": 5, "operation": "Entity linking", "detail": f"Linked to SNOMED CT / HGNC / HGVS / ClinVar / LOINC ({len(set(e.vocabulary for e in kept))} vocabularies)", "count": linked},
            {"step": 6, "operation": "Context detection (MetaCAT-style)", "detail": f"Negation={sum(1 for e in kept if e.negated)}, Historical={sum(1 for e in kept if e.historical)}, Family={sum(1 for e in kept if e.subject=='family')}", "count": len(kept)},
            {"step": 7, "operation": f"Confidence threshold ≥ {threshold:.2f}", "detail": f"{len(kept)} entities passed, {dropped} below threshold", "count": len(kept)},
            {"step": 8, "operation": "Structured export ready", "detail": "Entities available as CSV / JSON / annotated HTML; flow into de-id → OMOP → cohort", "count": len(kept)},
        ]

    # ----- exports ------------------------------------------------------- #

    @staticmethod
    def to_csv(entities: List[Dict[str, Any]]) -> str:
        import csv
        import io
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "span_text", "entity_type", "layer", "vocabulary", "concept",
            "code", "confidence", "negated", "historical", "subject", "context",
        ])
        for e in entities:
            writer.writerow([
                e["text"], e["entity_type_label"], e["layer"], e["vocabulary"],
                e["concept"], e["code"], e["confidence"],
                "yes" if e["negated"] else "no",
                "yes" if e["historical"] else "no",
                e["subject"], e["context"].replace("\n", " ").strip(),
            ])
        return buf.getvalue()

    # ----- sample documents ---------------------------------------------- #

    def list_samples(self) -> List[Dict[str, str]]:
        return [
            {"id": "icu_discharge", "title": "ICU Discharge Summary (general)", "type": "Clinical narrative",
             "description": "Cardiac ICU discharge summary — exercises the SNOMED clinical layer (conditions, procedures, labs, sites)."},
            {"id": "molecular_pathology", "title": "Molecular Pathology Report (genomic)", "type": "Molecular pathology",
             "description": "Lung adenocarcinoma NGS report — exercises SNOMED clinical layer + HGNC/HGVS/ClinVar molecular layer, with a negated finding."},
        ]

    def get_sample(self, sample_id: str) -> str:
        if sample_id == "molecular_pathology":
            return self._sample_molecular_pathology()
        return self._sample_icu_discharge()

    @staticmethod
    def _sample_icu_discharge() -> str:
        return """CARDIAC ICU DISCHARGE SUMMARY  (SYNTHETIC — NOT A REAL PATIENT)

CHIEF COMPLAINT:
Acute chest pain and shortness of breath.

HISTORY OF PRESENT ILLNESS:
The patient presented with acute substernal chest pain and dyspnea. A 12-lead ECG
showed ST-segment depression. Troponin I was elevated. The patient was diagnosed
with a non-ST elevation myocardial infarction (NSTEMI).

PAST MEDICAL HISTORY:
1. Type 2 diabetes mellitus, diagnosed in 2015.
2. Essential hypertension.
3. Hyperlipidemia.
4. Coronary artery disease with previous percutaneous coronary intervention in 2020.

FAMILY HISTORY:
Father with myocardial infarction at age 62. Mother with type 2 diabetes mellitus.

HOSPITAL COURSE:
The patient underwent cardiac catheterization, which demonstrated a critical lesion
of the left anterior descending coronary artery. A drug-eluting stent was placed.
An echocardiogram showed anterior wall hypokinesis. There was no evidence of
pulmonary congestion on the post-procedure chest film. Mechanical ventilation was
not required.

LABORATORY DATA:
Troponin I peaked and then trended down over serial measurements. HbA1c was 7.8%.
LDL cholesterol was elevated. Creatinine remained at baseline; there was no acute
kidney injury.

DISCHARGE MEDICATIONS:
Aspirin, clopidogrel, high-intensity atorvastatin, metoprolol, lisinopril, and
metformin. Nitroglycerin was prescribed as needed for chest pain.
"""

    @staticmethod
    def _sample_molecular_pathology() -> str:
        return """MOLECULAR PATHOLOGY REPORT  (SYNTHETIC — NOT A REAL PATIENT)

SPECIMEN:
CT-guided core needle biopsy of a mass in the left upper lobe of the lung.

CLINICAL HISTORY:
Adult patient with a left upper lobe lung mass. No prior history of malignancy.

GROSS / MICROSCOPIC DESCRIPTION:
Sections of lung parenchyma show an infiltrating poorly differentiated
adenocarcinoma. Lymphovascular invasion is present. The findings are consistent
with a primary adenocarcinoma of the lung (non-small cell lung cancer).
Immunohistochemistry supports a pulmonary primary.

MOLECULAR DIAGNOSTICS:
Next-generation sequencing was performed on tumor tissue.
- EGFR: exon 19 deletion (p.Glu746_Ala750del) detected — EGFR gene mutation positive.
- ALK: no rearrangement detected.
- ROS1: negative.
- KRAS: no mutation detected.
EGFR mutation analysis confirms an EGFR-TKI sensitizing alteration.

IMMUNOHISTOCHEMISTRY:
PD-L1 immunohistochemistry: tumor proportion score (TPS) 80%.

INTEGRATED DIAGNOSIS:
Adenocarcinoma of the lung, left upper lobe, EGFR exon 19 deletion positive,
ALK negative, ROS1 negative, PD-L1 TPS 80%. Findings support consideration of
osimertinib; pembrolizumab may be considered given high PD-L1 expression.

NOTE: All molecular codes (HGNC / HGVS / ClinVar) and SNOMED concepts are
ILLUSTRATIVE and must be validated against a live terminology server before use.
"""
