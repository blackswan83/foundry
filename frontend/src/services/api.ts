// Use environment variable for API URL, fallback to relative path for same-origin
const API_BASE = import.meta.env.VITE_API_URL || '/api';

export interface PipelineResult {
  pipeline_steps: Array<{
    step: number;
    name: string;
    status: string;
    result: Record<string, unknown>;
  }>;
  overall_status: string;
  message?: string;
  error?: string;
}

export interface CohortResult {
  cohort_name: string;
  description: string;
  member_count: number;
  member_ids: number[];
  statistics: {
    demographics: {
      total_count: number;
      male_count: number;
      female_count: number;
      male_percentage: number;
      age_mean: number;
      age_min: number;
      age_max: number;
    };
    clinical: {
      total_visits: number;
      visits_per_person: number;
      total_conditions: number;
      conditions_per_person: number;
    };
  };
}

export interface PatientInfo {
  person_id: number;
  age: number;
  gender: string;
  region: string;
  display_name: string;
}

export interface PatientListResponse {
  total_patients: number;
  patients: PatientInfo[];
}

export interface PatientAnalysis {
  patient_token: string;
  summary: {
    demographics: { age: number; gender: string };
    clinical_summary: {
      total_visits: number;
      active_conditions: string[];
      current_medications: string[];
      recent_lab_count: number;
    };
  };
  insights: Array<{
    type: string;
    severity: string;
    title: string;
    description: string;
    evidence: string[];
    recommendations: string[];
  }>;
  risk_score: {
    score: number;
    level: string;
    color: string;
    breakdown: {
      high_severity_findings: number;
      medium_severity_findings: number;
      low_severity_findings: number;
    };
  };
}

export const api = {
  async runFullPipeline(numPatients: number = 30): Promise<PipelineResult> {
    const response = await fetch(`${API_BASE}/demo/full-pipeline?num_patients=${numPatients}`, {
      method: 'POST',
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Pipeline failed: ${response.status} - ${text}`);
    }
    return response.json();
  },

  async getStatus(): Promise<Record<string, boolean | string[]>> {
    const response = await fetch(`${API_BASE}/demo/status`);
    return response.json();
  },

  async resetDemo(): Promise<void> {
    await fetch(`${API_BASE}/demo/reset`, { method: 'DELETE' });
  },

  async getLinkageDemo(): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/demo/linkage-demo`);
    return response.json();
  },

  async getDeidentificationDemo(): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/demo/deidentification-demo`);
    return response.json();
  },

  async getOMOPTransformationDemo(): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/demo/omop-transformation-demo`);
    return response.json();
  },

  async getAvailableQueries(): Promise<{ queries: Array<{ id: string; name: string; description: string }> }> {
    const response = await fetch(`${API_BASE}/demo/cohort/available-queries`);
    return response.json();
  },

  async runCohortQuery(queryName: string): Promise<{ cohort_result: CohortResult }> {
    const response = await fetch(`${API_BASE}/demo/cohort/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_name: queryName }),
    });
    if (!response.ok) throw new Error('Query failed');
    return response.json();
  },

  async getAnalytics(): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/demo/cohort/analytics`);
    return response.json();
  },

  async analyzePatient(personId: number): Promise<{ analysis: PatientAnalysis }> {
    const response = await fetch(`${API_BASE}/demo/ai/analyze-patient/${personId}`);
    if (!response.ok) throw new Error('Analysis failed');
    return response.json();
  },

  async analyzeCohort(queryName: string): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/demo/ai/analyze-cohort`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_name: queryName }),
    });
    return response.json();
  },

  async uploadCSV(file: File): Promise<{
    status: string;
    message: string;
    parsing: {
      total_rows: number;
      valid_rows: number;
      errors: string[];
      warnings: string[];
    };
    deidentification: {
      patients_processed: number;
      method: string;
    };
    download_available: boolean;
  }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/demo/upload-csv`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.message || error.detail || 'Upload failed');
    }

    return response.json();
  },

  async downloadDeidentifiedCSV(): Promise<Blob> {
    const response = await fetch(`${API_BASE}/demo/download-csv`);
    if (!response.ok) {
      throw new Error('Download failed - no de-identified data available');
    }
    return response.blob();
  },

  async getQualityMetrics(): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/demo/quality-metrics`);
    if (!response.ok) throw new Error('Failed to fetch quality metrics');
    return response.json();
  },

  async getDataQuality(): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/demo/data-quality`);
    if (!response.ok) throw new Error('Failed to fetch data quality');
    return response.json();
  },

  async getExecutiveSummary(): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/demo/executive-summary`);
    if (!response.ok) throw new Error('Failed to fetch executive summary');
    return response.json();
  },

  async getReadmissionRisk(personId: number): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/demo/readmission-risk/${personId}`);
    if (!response.ok) throw new Error('Failed to fetch readmission risk');
    return response.json();
  },

  async getPatientList(): Promise<PatientListResponse> {
    const response = await fetch(`${API_BASE}/demo/patient-list`);
    if (!response.ok) throw new Error('Failed to fetch patient list');
    return response.json();
  },
};
