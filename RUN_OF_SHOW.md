# Nuraxi Elembic — Demo Run-of-Show (v1.1)

For the KFSHRC genomic-team review. Guiding principle (Petros): **substance over
polish** — *"here's the output, here are the operations that were performed."*
Every screen makes inputs, transformations, and outputs explicit and exportable.

> **Honesty guardrails (state these if asked):**
> - All data on screen is **synthetic** — no real PHI anywhere.
> - The extraction engine mirrors the real Elembic stack (MedCAT for NER+L, a
>   MetaCAT-style layer for negation/temporality/experiencer) but runs a curated,
>   deterministic dictionary+rule engine in the demo so it is reproducible
>   offline — no live model weights are loaded.
> - Every SNOMED / HGNC / HGVS / ClinVar / LOINC code shown is **illustrative**
>   and must be validated against a live terminology server before production.
>   This is surfaced on-screen in the Text Extraction tab.

---

## Order of walkthrough (~10–12 min)

1. **One-line framing** (Home tab)
   "Fragmented clinical data → AI-ready." Scroll the landing page: the 6-step
   flow now **leads with Clinical Text Extraction**.

2. **Clinical Text Extraction (NEW — lead with this; it is the differentiator).**
   Tab: **Text Extraction**.
   - Select the **Molecular Pathology Report (genomic)** sample.
   - Click **Extract & Annotate**. Walk the three panels:
     - **Left** — the raw, unstructured note.
     - **Center** — the same note with entities highlighted inline; **hover** a
       span to show the linked concept, vocabulary + code, confidence, and the
       context flags (negated / historical / patient-vs-family).
     - **Right** — the structured entity table (span | type | concept | code |
       confidence | flags).
   - Point out the **two layers, on purpose**:
     - **Clinical layer → SNOMED CT**: *Adenocarcinoma of lung* (254626006),
       *Structure of left upper lobe of lung* (45653009), *Core needle biopsy*
       (67800003).
     - **Molecular layer → genomic vocabularies**: *EGFR* (**HGNC:3236**), *exon
       19 deletion* (**HGVS** p.Glu746_Ala750del, ClinVar: pathogenic / TKI-
       sensitizing), *PD-L1 TPS*.
   - Show **context detection**: `ALK`, `ROS1`, `KRAS` are flagged **negated**
     ("no rearrangement detected" / "negative"); the EGFR alteration is affirmed.
   - Scroll to **Operations performed (audit trail)** — document parsed →
     segmentation → NER → linking → context detection → confidence threshold →
     export. Drag the **confidence threshold** slider to show entities drop out.
   - Click **Download CSV** (Petros asked for this), then JSON / annotated HTML /
     operations log. Note these coded entities **flow into** de-id → OMOP → cohort.
   - Optionally switch to the **ICU Discharge Summary (general)** sample to show
     breadth, or pick **Paste your own** to run their text live.

3. **De-identification before/after** (Tab: **De-identification**).
   - Run the pipeline first (Pipeline tab → Run Full Pipeline) so demos populate.
   - Original PHI vs de-identified. The **count of identifiers removed matches
     the enumerated list**, and "18" now correctly labels *PDPL identifier
     categories addressed*. Dates of birth are reduced to **year only** (strict
     Safe Harbor); be ready for the re-identification question.

4. **OMOP transform** (Tab: **OMOP Transform**) — real concept mappings:
   ICD-10 → SNOMED, labs → LOINC, meds → RxNorm.

5. **Cohort query → aggregate stats** (Tab: **Cohort Queries**) — pick a cohort,
   show demographics/clinical aggregates. **N is consistent: 30 unique patients**
   from 57 source records (27 duplicate records linked across systems).

6. **Close on exports + audit trail** — "here's the output, here are the
   operations." Mention AI Insights now renders **human-readable lab names**
   (e.g., *Creatinine (2160-0)*), defensible trend logic (≥3 serial
   measurements), and finding-specific recommendations.

---

## Numbers to keep straight (single source of truth)

| Figure | Value | Meaning |
|---|---|---|
| **Unique patients (N)** | **30** | de-duplicated PERSON table; shown on every patient stage |
| Source records | 57 | records ingested across 4 systems before linkage |
| Duplicate records linked | 27 | 57 − 30 |

The header, every pipeline stage, OMOP, the cohort query, and the executive
dashboard all report **30** as the patient count. The 57 is always labelled
*source records*, never "patients".

---

## Genomic sample — expected extraction (talking points)

A synthetic lung-adenocarcinoma molecular-pathology note surfaces, by design:

- morphology / condition → SNOMED (*adenocarcinoma of lung*, *non-small cell lung cancer*)
- anatomical site → SNOMED (*left upper lobe of lung*, *lung structure*)
- procedure → SNOMED (*core needle biopsy*, *immunohistochemistry*, *NGS*)
- gene → **HGNC** (*EGFR*, *ALK*, *ROS1*, *KRAS*, *CD274/PD-L1*)
- variant → **HGVS** (*EGFR exon 19 deletion* p.Glu746_Ala750del)
- clinical significance → **ClinVar** (pathogenic / TKI-sensitizing)
- at least one **negated** finding (*ALK / ROS1 / KRAS* negative) to demonstrate
  context detection

> SNOMED is the clinical layer; HGNC/HGVS/ClinVar are the molecular layer.
> Showing we understand the distinction lands better with a genomic team than
> forcing everything into SNOMED.
