"""
Cohort Query Service

Enables research queries and analytics on the OMOP-transformed data.
Supports building patient cohorts based on clinical criteria.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum


class CriterionType(str, Enum):
    """Types of cohort criteria."""
    DIAGNOSIS = "diagnosis"
    MEDICATION = "medication"
    LAB_VALUE = "lab_value"
    AGE = "age"
    GENDER = "gender"
    VISIT_TYPE = "visit_type"


class Operator(str, Enum):
    """Comparison operators for criteria."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"


@dataclass
class CohortCriterion:
    """A single criterion for cohort selection."""
    criterion_type: CriterionType
    field: str
    operator: Operator
    value: Any
    value_high: Optional[Any] = None  # For BETWEEN operator


@dataclass
class CohortDefinition:
    """Definition of a research cohort."""
    name: str
    description: str
    inclusion_criteria: List[CohortCriterion]
    exclusion_criteria: List[CohortCriterion]


class CohortQueryService:
    """
    Service for querying and building research cohorts from OMOP data.
    """

    # Common OMOP concept IDs for demo queries
    CONCEPT_MAPPINGS = {
        # Conditions (SNOMED)
        "diabetes": 44054006,
        "hypertension": 38341003,
        "heart_failure": 84114007,
        "ckd": 709044004,
        "esrd": 46177005,
        "leukemia": 93143009,
        "breast_cancer": 254837009,
        "lymphoma": 118601006,

        # Measurements (LOINC -> OMOP)
        "hemoglobin": 3000963,
        "creatinine": 3016723,
        "glucose": 3004501,
        "hba1c": 3004410,
        "wbc": 3010813,
        "platelets": 3024929,

        # Drugs (RxNorm -> OMOP)
        "metformin": 19078461,
        "insulin": 35894915,
        "lisinopril": 1308216,
        "tacrolimus": 950637,

        # Visit types
        "inpatient": 9201,
        "outpatient": 9202,
        "emergency": 9203,

        # Gender
        "male": 8507,
        "female": 8532,
    }

    def __init__(self):
        self._omop_data: Dict[str, List[Dict]] = {}
        self._query_log: List[Dict] = []

    def load_omop_data(self, omop_data: Dict[str, List[Dict]]):
        """Load OMOP data for querying."""
        self._omop_data = omop_data

    def _evaluate_criterion(
        self,
        person_id: int,
        criterion: CohortCriterion,
    ) -> bool:
        """Evaluate a single criterion for a person."""
        if criterion.criterion_type == CriterionType.AGE:
            return self._evaluate_age_criterion(person_id, criterion)
        elif criterion.criterion_type == CriterionType.GENDER:
            return self._evaluate_gender_criterion(person_id, criterion)
        elif criterion.criterion_type == CriterionType.DIAGNOSIS:
            return self._evaluate_diagnosis_criterion(person_id, criterion)
        elif criterion.criterion_type == CriterionType.MEDICATION:
            return self._evaluate_medication_criterion(person_id, criterion)
        elif criterion.criterion_type == CriterionType.LAB_VALUE:
            return self._evaluate_lab_criterion(person_id, criterion)
        elif criterion.criterion_type == CriterionType.VISIT_TYPE:
            return self._evaluate_visit_criterion(person_id, criterion)
        return False

    def _evaluate_age_criterion(
        self,
        person_id: int,
        criterion: CohortCriterion,
    ) -> bool:
        """Evaluate age criterion."""
        persons = self._omop_data.get("person", [])
        person = next((p for p in persons if p["person_id"] == person_id), None)
        if not person:
            return False

        year_of_birth = person.get("year_of_birth", 1900)
        current_year = datetime.now().year
        age = current_year - year_of_birth

        if criterion.operator == Operator.EQUALS:
            return age == criterion.value
        elif criterion.operator == Operator.GREATER_THAN:
            return age > criterion.value
        elif criterion.operator == Operator.LESS_THAN:
            return age < criterion.value
        elif criterion.operator == Operator.BETWEEN:
            return criterion.value <= age <= criterion.value_high
        return False

    def _evaluate_gender_criterion(
        self,
        person_id: int,
        criterion: CohortCriterion,
    ) -> bool:
        """Evaluate gender criterion."""
        persons = self._omop_data.get("person", [])
        person = next((p for p in persons if p["person_id"] == person_id), None)
        if not person:
            return False

        gender_concept = person.get("gender_concept_id", 0)

        if criterion.operator == Operator.EQUALS:
            target = self.CONCEPT_MAPPINGS.get(criterion.value, criterion.value)
            return gender_concept == target
        return False

    def _evaluate_diagnosis_criterion(
        self,
        person_id: int,
        criterion: CohortCriterion,
    ) -> bool:
        """Evaluate diagnosis criterion."""
        conditions = self._omop_data.get("condition_occurrence", [])
        person_conditions = [c for c in conditions if c["person_id"] == person_id]

        if criterion.operator == Operator.IN:
            # Handle list of values for IN operator
            targets = [self.CONCEPT_MAPPINGS.get(v, v) for v in criterion.value]
            return any(c["condition_concept_id"] in targets for c in person_conditions)
        else:
            # Single value for EXISTS/EQUALS
            target_concept = self.CONCEPT_MAPPINGS.get(criterion.value, criterion.value)
            if criterion.operator == Operator.EXISTS:
                return any(c["condition_concept_id"] == target_concept for c in person_conditions)
            elif criterion.operator == Operator.EQUALS:
                return any(c["condition_concept_id"] == target_concept for c in person_conditions)
        return False

    def _evaluate_medication_criterion(
        self,
        person_id: int,
        criterion: CohortCriterion,
    ) -> bool:
        """Evaluate medication criterion."""
        drugs = self._omop_data.get("drug_exposure", [])
        person_drugs = [d for d in drugs if d["person_id"] == person_id]

        target_concept = self.CONCEPT_MAPPINGS.get(criterion.value, criterion.value)

        if criterion.operator == Operator.EXISTS:
            return any(d["drug_concept_id"] == target_concept for d in person_drugs)
        elif criterion.operator == Operator.EQUALS:
            return any(d["drug_concept_id"] == target_concept for d in person_drugs)
        return False

    def _evaluate_lab_criterion(
        self,
        person_id: int,
        criterion: CohortCriterion,
    ) -> bool:
        """Evaluate lab value criterion."""
        measurements = self._omop_data.get("measurement", [])
        person_measurements = [m for m in measurements if m["person_id"] == person_id]

        # Find measurements matching the lab type
        target_concept = self.CONCEPT_MAPPINGS.get(criterion.field, criterion.field)
        matching_labs = [
            m for m in person_measurements
            if m["measurement_concept_id"] == target_concept
        ]

        if not matching_labs:
            return False

        # Get the most recent value
        latest = max(matching_labs, key=lambda m: m.get("measurement_datetime", ""))
        value = latest.get("value_as_number")

        if value is None:
            return False

        if criterion.operator == Operator.GREATER_THAN:
            return value > criterion.value
        elif criterion.operator == Operator.LESS_THAN:
            return value < criterion.value
        elif criterion.operator == Operator.BETWEEN:
            return criterion.value <= value <= criterion.value_high
        elif criterion.operator == Operator.EQUALS:
            return value == criterion.value
        return False

    def _evaluate_visit_criterion(
        self,
        person_id: int,
        criterion: CohortCriterion,
    ) -> bool:
        """Evaluate visit type criterion."""
        visits = self._omop_data.get("visit_occurrence", [])
        person_visits = [v for v in visits if v["person_id"] == person_id]

        target_concept = self.CONCEPT_MAPPINGS.get(criterion.value, criterion.value)

        if criterion.operator == Operator.EXISTS:
            return any(v["visit_concept_id"] == target_concept for v in person_visits)
        elif criterion.operator == Operator.EQUALS:
            return any(v["visit_concept_id"] == target_concept for v in person_visits)
        return False

    def build_cohort(
        self,
        definition: CohortDefinition,
    ) -> Dict[str, Any]:
        """
        Build a cohort based on the given definition.
        Returns cohort members and statistics.
        """
        persons = self._omop_data.get("person", [])
        all_person_ids = {p["person_id"] for p in persons}

        # Apply inclusion criteria
        included = set()
        for person_id in all_person_ids:
            meets_all = all(
                self._evaluate_criterion(person_id, criterion)
                for criterion in definition.inclusion_criteria
            )
            if meets_all:
                included.add(person_id)

        # Apply exclusion criteria
        excluded = set()
        for person_id in included:
            meets_any = any(
                self._evaluate_criterion(person_id, criterion)
                for criterion in definition.exclusion_criteria
            )
            if meets_any:
                excluded.add(person_id)

        cohort_members = included - excluded

        # Log the query
        self._query_log.append({
            "cohort_name": definition.name,
            "timestamp": datetime.now().isoformat(),
            "total_persons": len(all_person_ids),
            "included": len(included),
            "excluded": len(excluded),
            "final_cohort": len(cohort_members),
        })

        # Calculate cohort statistics
        stats = self._calculate_cohort_statistics(list(cohort_members))

        return {
            "cohort_name": definition.name,
            "description": definition.description,
            "member_count": len(cohort_members),
            "member_ids": list(cohort_members),
            "statistics": stats,
            "criteria_summary": {
                "inclusion": [
                    {
                        "type": c.criterion_type.value,
                        "field": c.field,
                        "operator": c.operator.value,
                        "value": c.value,
                    }
                    for c in definition.inclusion_criteria
                ],
                "exclusion": [
                    {
                        "type": c.criterion_type.value,
                        "field": c.field,
                        "operator": c.operator.value,
                        "value": c.value,
                    }
                    for c in definition.exclusion_criteria
                ],
            },
        }

    def _calculate_cohort_statistics(
        self,
        person_ids: List[int],
    ) -> Dict[str, Any]:
        """Calculate statistics for a cohort."""
        if not person_ids:
            return {"error": "Empty cohort"}

        persons = self._omop_data.get("person", [])
        cohort_persons = [p for p in persons if p["person_id"] in person_ids]

        # Age statistics
        current_year = datetime.now().year
        ages = [current_year - p.get("year_of_birth", current_year) for p in cohort_persons]

        # Gender distribution
        male_count = sum(1 for p in cohort_persons if p.get("gender_concept_id") == 8507)
        female_count = sum(1 for p in cohort_persons if p.get("gender_concept_id") == 8532)

        # Visit statistics
        visits = self._omop_data.get("visit_occurrence", [])
        cohort_visits = [v for v in visits if v["person_id"] in person_ids]

        # Condition statistics
        conditions = self._omop_data.get("condition_occurrence", [])
        cohort_conditions = [c for c in conditions if c["person_id"] in person_ids]

        return {
            "demographics": {
                "total_count": len(person_ids),
                "male_count": male_count,
                "female_count": female_count,
                "male_percentage": round(male_count / len(person_ids) * 100, 1) if person_ids else 0,
                "age_mean": round(sum(ages) / len(ages), 1) if ages else 0,
                "age_min": min(ages) if ages else 0,
                "age_max": max(ages) if ages else 0,
            },
            "clinical": {
                "total_visits": len(cohort_visits),
                "visits_per_person": round(len(cohort_visits) / len(person_ids), 1) if person_ids else 0,
                "total_conditions": len(cohort_conditions),
                "conditions_per_person": round(len(cohort_conditions) / len(person_ids), 1) if person_ids else 0,
            },
        }

    def run_predefined_query(
        self,
        query_name: str,
    ) -> Dict[str, Any]:
        """Run a predefined research query."""
        # Special case: all_patients returns everyone
        if query_name == "all_patients":
            persons = self._omop_data.get("person", [])
            all_ids = [p["person_id"] for p in persons]
            stats = self._calculate_cohort_statistics(all_ids)
            return {
                "cohort_name": "All Patients",
                "description": "All patients in the dataset",
                "member_count": len(all_ids),
                "member_ids": all_ids,
                "statistics": stats,
                "criteria_summary": {"inclusion": [], "exclusion": []},
            }

        predefined_queries = {
            "diabetic_patients": CohortDefinition(
                name="Diabetic Patients",
                description="Patients with Type 2 Diabetes diagnosis",
                inclusion_criteria=[
                    CohortCriterion(
                        criterion_type=CriterionType.DIAGNOSIS,
                        field="condition",
                        operator=Operator.EXISTS,
                        value="diabetes",
                    ),
                ],
                exclusion_criteria=[],
            ),
            "ckd_on_dialysis": CohortDefinition(
                name="CKD Patients on Dialysis",
                description="Patients with CKD/ESRD potentially on dialysis",
                inclusion_criteria=[
                    CohortCriterion(
                        criterion_type=CriterionType.DIAGNOSIS,
                        field="condition",
                        operator=Operator.IN,
                        value=["ckd", "esrd"],
                    ),
                ],
                exclusion_criteria=[],
            ),
            "transplant_patients": CohortDefinition(
                name="Transplant Recipients",
                description="Patients on immunosuppression (likely transplant)",
                inclusion_criteria=[
                    CohortCriterion(
                        criterion_type=CriterionType.MEDICATION,
                        field="drug",
                        operator=Operator.EXISTS,
                        value="tacrolimus",
                    ),
                ],
                exclusion_criteria=[],
            ),
            "oncology_patients": CohortDefinition(
                name="Oncology Patients",
                description="Patients with cancer diagnoses",
                inclusion_criteria=[
                    CohortCriterion(
                        criterion_type=CriterionType.DIAGNOSIS,
                        field="condition",
                        operator=Operator.IN,
                        value=["leukemia", "breast_cancer", "lymphoma"],
                    ),
                ],
                exclusion_criteria=[],
            ),
            "elderly_cardiac": CohortDefinition(
                name="Elderly Cardiac Patients",
                description="Patients 65+ with heart failure",
                inclusion_criteria=[
                    CohortCriterion(
                        criterion_type=CriterionType.AGE,
                        field="age",
                        operator=Operator.GREATER_THAN,
                        value=64,
                    ),
                    CohortCriterion(
                        criterion_type=CriterionType.DIAGNOSIS,
                        field="condition",
                        operator=Operator.EXISTS,
                        value="heart_failure",
                    ),
                ],
                exclusion_criteria=[],
            ),
        }

        if query_name not in predefined_queries:
            return {
                "error": f"Unknown query: {query_name}",
                "available_queries": list(predefined_queries.keys()),
            }

        return self.build_cohort(predefined_queries[query_name])

    # SNOMED concept ID to display name mapping
    CONDITION_NAMES = {
        0: "Unmapped/Other",
        44054006: "Type 2 Diabetes",
        38341003: "Hypertension",
        84114007: "Heart Failure",
        709044004: "Chronic Kidney Disease",
        46177005: "End-Stage Renal Disease",
        93143009: "Acute Lymphoid Leukemia",
        254837009: "Breast Cancer",
        118601006: "Non-Hodgkin Lymphoma",
        109989006: "Multiple Myeloma",
        53741008: "Coronary Artery Disease",
        233604007: "Pneumonia",
        91302008: "Sepsis",
        14669001: "Acute Kidney Injury",
        230690007: "Stroke",
        22298006: "Myocardial Infarction",
        59282003: "Pulmonary Embolism",
        128053003: "Deep Vein Thrombosis",
        25370001: "Hepatocellular Carcinoma",
        363406005: "Colon Cancer",
        19943007: "Cirrhosis",
        417357006: "Sickle Cell Disease",
        40108008: "Thalassemia Major",
    }

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get overall analytics summary of the data."""
        persons = self._omop_data.get("person", [])
        visits = self._omop_data.get("visit_occurrence", [])
        conditions = self._omop_data.get("condition_occurrence", [])
        measurements = self._omop_data.get("measurement", [])
        drugs = self._omop_data.get("drug_exposure", [])

        # Condition frequency
        condition_counts: Dict[int, int] = {}
        for c in conditions:
            concept_id = c.get("condition_concept_id", 0)
            condition_counts[concept_id] = condition_counts.get(concept_id, 0) + 1

        # Drug frequency
        drug_counts: Dict[int, int] = {}
        for d in drugs:
            concept_id = d.get("drug_concept_id", 0)
            drug_counts[concept_id] = drug_counts.get(concept_id, 0) + 1

        # Reverse lookup for drug names
        reverse_drugs = {v: k for k, v in self.CONCEPT_MAPPINGS.items() if isinstance(v, int)}

        top_conditions = sorted(condition_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_drugs = sorted(drug_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "data_summary": {
                "total_persons": len(persons),
                "total_visits": len(visits),
                "total_conditions": len(conditions),
                "total_measurements": len(measurements),
                "total_drug_exposures": len(drugs),
            },
            "top_conditions": [
                {
                    "concept_id": concept_id,
                    "name": self.CONDITION_NAMES.get(concept_id, f"SNOMED {concept_id}"),
                    "count": count,
                }
                for concept_id, count in top_conditions
            ],
            "top_medications": [
                {
                    "concept_id": concept_id,
                    "name": reverse_drugs.get(concept_id, f"RxNorm {concept_id}"),
                    "count": count,
                }
                for concept_id, count in top_drugs
            ],
            "query_history": self._query_log[-10:],  # Last 10 queries
        }

    def get_available_queries(self) -> List[Dict[str, str]]:
        """Get list of available predefined queries."""
        return [
            {"id": "all_patients", "name": "All Patients", "description": "All patients in dataset"},
            {"id": "diabetic_patients", "name": "Diabetic Patients", "description": "Patients with Type 2 Diabetes"},
            {"id": "ckd_on_dialysis", "name": "CKD Patients", "description": "Chronic Kidney Disease patients"},
            {"id": "transplant_patients", "name": "Transplant Recipients", "description": "Patients on immunosuppression"},
            {"id": "oncology_patients", "name": "Oncology Patients", "description": "Cancer patients"},
            {"id": "elderly_cardiac", "name": "Elderly Cardiac", "description": "65+ with heart failure"},
        ]
