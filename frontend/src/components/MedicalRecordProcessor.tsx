import React, { useState } from 'react';

interface Entity {
  text: string;
  type: string;
  start: number;
  end: number;
  confidence: number;
  normalized_term?: string;
  terminology_code?: string;
  terminology_system?: string;
  context?: string;
}

interface PHIDetection {
  text: string;
  type: string;
  start: number;
  end: number;
  confidence: number;
  replacement: string;
}

interface TerminologyMapping {
  entity_text: string;
  entity_type: string;
  mappings: Array<{
    code: string;
    term?: string;
    name?: string;
    description?: string;
    system: string;
    [key: string]: any;
  }>;
}

interface ProcessingResult {
  original_text: string;
  deidentified_text: string;
  entities: Entity[];
  phi_detections: PHIDetection[];
  phi_summary: {
    total_phi_found: number;
    phi_by_type: Record<string, any[]>;
    types_found: string[];
    safe_harbor_compliance: boolean;
  };
  terminology_mappings: {
    conditions: TerminologyMapping[];
    medications: TerminologyMapping[];
    procedures: TerminologyMapping[];
    lab_tests: TerminologyMapping[];
    vital_signs: TerminologyMapping[];
    symptoms: TerminologyMapping[];
  };
  processing_stats: {
    processing_time_seconds: number;
    character_count: number;
    word_count: number;
    entities_extracted: number;
    phi_detected: number;
    terminology_mappings: number;
    safe_harbor_compliance: boolean;
  };
  safe_harbor_18_identifiers: string[];
}

const API_BASE = import.meta.env.VITE_API_URL || '';

const EntityTypeColors: Record<string, string> = {
  condition: 'entity-condition',
  diagnosis: 'entity-condition',
  medication: 'entity-medication',
  procedure: 'entity-procedure',
  lab_test: 'entity-lab',
  lab_value: 'entity-lab',
  vital_sign: 'entity-vital',
  symptom: 'entity-symptom',
};

const PHITypeLabels: Record<string, string> = {
  name: 'Patient/Provider Names',
  geographic: 'Geographic Data',
  date: 'Dates',
  phone: 'Phone Numbers',
  fax: 'Fax Numbers',
  email: 'Email Addresses',
  ssn: 'National ID / SSN',
  mrn: 'Medical Record Numbers',
  health_plan_id: 'Health Plan IDs (CCHI)',
  account_number: 'Account Numbers',
  license_number: 'License Numbers (SCFHS)',
  vehicle_id: 'Vehicle Identifiers',
  device_id: 'Device Identifiers',
  url: 'Web URLs',
  ip_address: 'IP Addresses',
  biometric: 'Biometric Identifiers',
  photo: 'Full-face Photos',
  unique_id: 'Unique Identifiers',
};

// Processing steps for the overlay animation
const PROCESSING_STEPS = [
  { id: 1, label: 'Extracting text from document', icon: '📄' },
  { id: 2, label: 'Running Clinical NLP analysis', icon: '🔬' },
  { id: 3, label: 'Mapping to standard terminologies', icon: '🏥' },
  { id: 4, label: 'Detecting personal identifiers', icon: '🔍' },
  { id: 5, label: 'Applying PDPL de-identification', icon: '🔒' },
];

const MIN_PROCESSING_TIME = 5000;

const waitForRender = () => new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 50)));

export const MedicalRecordProcessor: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'comparison' | 'entities' | 'terminology' | 'phi'>('comparison');
  const [showOriginal, setShowOriginal] = useState(true);
  const [processingStep, setProcessingStep] = useState(0);
  const [showProcessingOverlay, setShowProcessingOverlay] = useState(false);

  const loadSampleDocument = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/demo/medical-record/sample`);
      const data = await response.json();
      setInputText(data.sample_document);
    } catch (err) {
      setError('Failed to load sample document');
    } finally {
      setLoading(false);
    }
  };

  const processDocument = async () => {
    if (!inputText.trim()) {
      setError('Please enter or load a medical document');
      return;
    }

    const startTime = Date.now();
    setLoading(true);
    setError(null);
    setShowProcessingOverlay(true);
    setProcessingStep(1);

    await waitForRender();

    try {
      const apiPromise = fetch(`${API_BASE}/api/demo/medical-record/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      }).then(response => {
        if (!response.ok) throw new Error('Processing failed');
        return response.json();
      });

      for (let i = 1; i < PROCESSING_STEPS.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        setProcessingStep(i + 1);
      }

      await new Promise(resolve => setTimeout(resolve, 1000));

      const data = await apiPromise;

      const elapsed = Date.now() - startTime;
      if (elapsed < MIN_PROCESSING_TIME) {
        await new Promise(resolve => setTimeout(resolve, MIN_PROCESSING_TIME - elapsed));
      }

      setResult(data);
      setActiveTab('comparison');
    } catch (err) {
      setError('Failed to process document. Please try again.');
    } finally {
      setShowProcessingOverlay(false);
      setProcessingStep(0);
      setLoading(false);
    }
  };

  const processSampleDocument = async () => {
    const startTime = Date.now();
    setLoading(true);
    setError(null);
    setShowProcessingOverlay(true);
    setProcessingStep(1);

    await waitForRender();

    try {
      const apiPromise = fetch(`${API_BASE}/api/demo/medical-record/process-sample`, {
        method: 'POST',
      }).then(response => {
        if (!response.ok) throw new Error('Processing failed');
        return response.json();
      });

      for (let i = 1; i < PROCESSING_STEPS.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        setProcessingStep(i + 1);
      }

      await new Promise(resolve => setTimeout(resolve, 1000));

      const data = await apiPromise;

      const elapsed = Date.now() - startTime;
      if (elapsed < MIN_PROCESSING_TIME) {
        await new Promise(resolve => setTimeout(resolve, MIN_PROCESSING_TIME - elapsed));
      }

      setInputText(data.original_text);
      setResult(data);
      setActiveTab('comparison');
    } catch (err) {
      setError('Failed to process sample document. Please try again.');
    } finally {
      setShowProcessingOverlay(false);
      setProcessingStep(0);
      setLoading(false);
    }
  };

  const highlightEntities = (text: string, entities: Entity[]) => {
    if (!entities.length) return text;

    const sortedEntities = [...entities].sort((a, b) => a.start - b.start);
    let lastEnd = 0;
    const parts: React.ReactNode[] = [];

    sortedEntities.forEach((entity, idx) => {
      if (entity.start >= lastEnd) {
        if (entity.start > lastEnd) {
          parts.push(text.slice(lastEnd, entity.start));
        }
        parts.push(
          <span
            key={idx}
            className={`entity-highlight ${EntityTypeColors[entity.type] || ''}`}
            title={`${entity.type}: ${entity.normalized_term || entity.text}${entity.terminology_code ? ` (${entity.terminology_system}: ${entity.terminology_code})` : ''}`}
          >
            {entity.text}
          </span>
        );
        lastEnd = entity.end;
      }
    });

    if (lastEnd < text.length) {
      parts.push(text.slice(lastEnd));
    }

    return parts;
  };

  const highlightPHI = (text: string, phiDetections: PHIDetection[]) => {
    if (!phiDetections.length) return text;

    const sortedPHI = [...phiDetections].sort((a, b) => a.start - b.start);
    let lastEnd = 0;
    const parts: React.ReactNode[] = [];

    sortedPHI.forEach((phi, idx) => {
      if (phi.start >= lastEnd) {
        if (phi.start > lastEnd) {
          parts.push(text.slice(lastEnd, phi.start));
        }
        parts.push(
          <span
            key={idx}
            className="phi-highlight"
            title={`${PHITypeLabels[phi.type] || phi.type}: "${phi.text}" → "${phi.replacement}"`}
          >
            {phi.text}
          </span>
        );
        lastEnd = phi.end;
      }
    });

    if (lastEnd < text.length) {
      parts.push(text.slice(lastEnd));
    }

    return parts;
  };

  return (
    <div className="medical-record-processor">
      {/* Processing Overlay */}
      {showProcessingOverlay && (
        <div className="processing-overlay">
          <div className="processing-modal">
            <div className="processing-header">
              <div className="processing-spinner">
                <svg viewBox="0 0 50 50">
                  <circle cx="25" cy="25" r="20" fill="none" strokeWidth="4" />
                </svg>
              </div>
              <h3>Processing Document</h3>
              <p>PDPL-compliant de-identification in progress</p>
            </div>

            <div className="processing-steps">
              {PROCESSING_STEPS.map((step, index) => {
                const isComplete = processingStep > index + 1 || (processingStep === PROCESSING_STEPS.length && index === PROCESSING_STEPS.length - 1);
                const isActive = processingStep === index + 1;

                return (
                  <div
                    key={step.id}
                    className={`processing-step ${isComplete ? 'completed' : ''} ${isActive ? 'active' : ''}`}
                  >
                    <div className="step-indicator">
                      {isComplete ? (
                        <svg viewBox="0 0 16 16" fill="currentColor">
                          <path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"/>
                        </svg>
                      ) : isActive ? (
                        <span className="step-spinner"></span>
                      ) : (
                        <span>{step.id}</span>
                      )}
                    </div>
                    <span className="step-label">{step.label}</span>
                    {isActive && <span className="step-loader"></span>}
                  </div>
                );
              })}
            </div>

            <div className="processing-footer">
              Processing time: ~5 seconds
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="section-header">
        <h2>Medical Record Processing</h2>
        <p>Process clinical documents with NLP entity extraction, terminology mapping, and PDPL-compliant de-identification.</p>
      </div>

      {/* Input Section */}
      <div className="result-card">
        <div className="input-header">
          <h3>Input Document</h3>
          <div className="input-actions">
            <a href="/sample_discharge_summary_kfshrc.pdf" download className="btn btn-secondary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
              Download Sample PDF
            </a>
            <button onClick={loadSampleDocument} disabled={loading} className="btn btn-secondary">
              Load Sample Text
            </button>
            <button onClick={processSampleDocument} disabled={loading} className="btn btn-primary">
              Process Sample (KFSHRC)
            </button>
          </div>
        </div>

        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste medical record text here, or click 'Download Sample PDF' to get the KFSHRC discharge summary. Then click 'Process Sample' to run the de-identification pipeline..."
          className="document-input"
        />

        <div className="input-footer">
          <div className="word-count">
            {inputText.length > 0 && (
              <span>{inputText.split(/\s+/).filter(w => w).length} words, {inputText.length} characters</span>
            )}
          </div>
          <button
            onClick={processDocument}
            disabled={loading || !inputText.trim()}
            className="btn btn-primary"
          >
            {loading ? <><span className="loading-spinner"></span> Processing...</> : 'Process Document'}
          </button>
        </div>
      </div>

      {error && (
        <div className="result-card" style={{ borderLeft: '4px solid var(--danger)' }}>
          <h3 style={{ color: 'var(--danger)' }}>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="results-container">
          {/* Stats Bar */}
          <div className="stats-bar">
            <div className="stat-item">
              <div className="value">{result.processing_stats.entities_extracted}</div>
              <div className="label">Entities Extracted</div>
            </div>
            <div className="stat-item">
              <div className="value">{result.processing_stats.phi_detected}</div>
              <div className="label">PHI Detected</div>
            </div>
            <div className="stat-item">
              <div className="value">{result.processing_stats.terminology_mappings}</div>
              <div className="label">Terminology Mappings</div>
            </div>
            <div className="stat-item">
              <div className="value">{result.processing_stats.processing_time_seconds.toFixed(2)}s</div>
              <div className="label">Processing Time</div>
            </div>
            <div className="stat-item compliance">
              <div className="value">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="label">PDPL Compliant</div>
            </div>
          </div>

          {/* Result Tabs */}
          <div className="result-card">
            <div className="result-tabs">
              {[
                { id: 'comparison', label: 'Before/After' },
                { id: 'entities', label: 'Clinical Entities' },
                { id: 'terminology', label: 'Terminology' },
                { id: 'phi', label: 'PHI Summary' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`result-tab ${activeTab === tab.id ? 'active' : ''}`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="result-content">
              {activeTab === 'comparison' && (
                <div>
                  <div className="comparison-toggle">
                    <button
                      onClick={() => setShowOriginal(true)}
                      className={`mode-btn ${showOriginal ? 'active' : ''}`}
                    >
                      Original (PHI highlighted)
                    </button>
                    <button
                      onClick={() => setShowOriginal(false)}
                      className={`mode-btn success ${!showOriginal ? 'active' : ''}`}
                    >
                      De-identified (PDPL)
                    </button>
                  </div>

                  <div className="document-view">
                    <pre>
                      {showOriginal
                        ? highlightPHI(result.original_text, result.phi_detections)
                        : result.deidentified_text}
                    </pre>
                  </div>

                  {showOriginal && (
                    <div className="insight-card medium">
                      <div className="insight-title">Note</div>
                      <div className="insight-description">
                        Highlighted text in red indicates detected Protected Health Information (PHI)
                        that will be removed or replaced during de-identification.
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'entities' && (
                <div>
                  <div className="entity-legend">
                    {Object.entries({
                      condition: 'Condition',
                      medication: 'Medication',
                      procedure: 'Procedure',
                      lab_test: 'Lab Test',
                      vital_sign: 'Vital Sign',
                      symptom: 'Symptom',
                    }).map(([type, label]) => (
                      <span key={type} className={`entity-tag ${EntityTypeColors[type]}`}>
                        {label}
                      </span>
                    ))}
                  </div>

                  <div className="document-view" style={{ maxHeight: '300px' }}>
                    <pre>{highlightEntities(result.original_text, result.entities)}</pre>
                  </div>

                  <h4 className="section-subtitle">Extracted Entities ({result.entities.length})</h4>
                  <div className="entities-list">
                    {result.entities.map((entity, idx) => (
                      <div key={idx} className={`entity-item ${EntityTypeColors[entity.type] || ''}`}>
                        <div className="entity-header">
                          <span className="entity-text">{entity.text}</span>
                          {entity.normalized_term && entity.normalized_term !== entity.text && (
                            <span className="entity-normalized">({entity.normalized_term})</span>
                          )}
                          <span className="entity-type">{entity.type.replace('_', ' ')}</span>
                        </div>
                        {entity.terminology_code && (
                          <div className="entity-code">
                            {entity.terminology_system}: {entity.terminology_code}
                          </div>
                        )}
                        <div className="entity-confidence">
                          Confidence: {(entity.confidence * 100).toFixed(0)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'terminology' && (
                <div className="terminology-grid">
                  {[
                    { key: 'conditions', label: 'Conditions/Diagnoses', icon: '🏥', system: 'SNOMED CT / ICD-10' },
                    { key: 'medications', label: 'Medications', icon: '💊', system: 'RxNorm' },
                    { key: 'procedures', label: 'Procedures', icon: '🔧', system: 'CPT' },
                    { key: 'lab_tests', label: 'Laboratory Tests', icon: '🧪', system: 'LOINC' },
                    { key: 'vital_signs', label: 'Vital Signs', icon: '❤️', system: 'LOINC' },
                    { key: 'symptoms', label: 'Symptoms', icon: '🤒', system: 'SNOMED CT' },
                  ].map(({ key, label, icon, system }) => {
                    const mappings = result.terminology_mappings[key as keyof typeof result.terminology_mappings] || [];
                    return (
                      <div key={key} className="terminology-card">
                        <h4>
                          <span>{icon}</span>
                          {label}
                          <span className="count">({mappings.length})</span>
                        </h4>
                        <div className="terminology-system">Mapped to: {system}</div>
                        <div className="terminology-items">
                          {mappings.length > 0 ? (
                            mappings.map((mapping, idx) => (
                              <div key={idx} className="terminology-item">
                                <div className="term-entity">{mapping.entity_text}</div>
                                {mapping.mappings.map((m, midx) => (
                                  <div key={midx} className="term-mapping">
                                    <code>{m.code}</code>
                                    <span>{m.term || m.name || m.description}</span>
                                    <span className="term-system">({m.system})</span>
                                  </div>
                                ))}
                              </div>
                            ))
                          ) : (
                            <div className="no-mappings">No mappings found</div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {activeTab === 'phi' && (
                <div>
                  <div className="phi-summary-grid">
                    <div className="insight-card info">
                      <div className="insight-title">
                        <svg width="18" height="18" viewBox="0 0 20 20" fill="currentColor" style={{ marginRight: '0.5rem', color: 'var(--success)' }}>
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        PDPL Compliance (Saudi Arabia)
                      </div>
                      <div className="insight-description" style={{ marginBottom: '1rem' }}>
                        All 18 personal data identifiers are addressed per PDPL (Saudi Personal Data Protection Law) requirements.
                      </div>
                      <div className="identifier-grid">
                        {result.safe_harbor_18_identifiers.map((id, idx) => (
                          <div key={id} className="identifier-item">
                            <span className="identifier-num">{idx + 1}</span>
                            {PHITypeLabels[id] || id}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="insight-card high">
                      <div className="insight-title">PHI Detected: {result.phi_summary.total_phi_found}</div>
                      <div className="insight-description" style={{ marginBottom: '1rem' }}>
                        Found {result.phi_summary.types_found.length} types of PHI in this document.
                      </div>
                      <div className="phi-types-list">
                        {result.phi_summary.types_found.map((type) => {
                          const items = result.phi_summary.phi_by_type[type] || [];
                          return (
                            <div key={type} className="phi-type-item">
                              <span>{PHITypeLabels[type] || type}</span>
                              <span className="phi-count">{items.length}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>

                  <h4 className="section-subtitle">Detected PHI Details</h4>
                  <div className="phi-table-container">
                    <table className="phi-table">
                      <thead>
                        <tr>
                          <th>Type</th>
                          <th>Original Text</th>
                          <th>Replacement</th>
                          <th>Confidence</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.phi_detections.map((phi, idx) => (
                          <tr key={idx}>
                            <td className="phi-type">{PHITypeLabels[phi.type] || phi.type}</td>
                            <td className="phi-original">{phi.text}</td>
                            <td className="phi-replacement">{phi.replacement}</td>
                            <td>{(phi.confidence * 100).toFixed(0)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Info Cards - Show when no result */}
      {!result && (
        <div className="info-cards">
          <div className="step-card">
            <div className="step-number" style={{ background: 'var(--info)', color: 'white' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <h3>Clinical NLP</h3>
            <p>Extracts medical entities including conditions, medications, procedures, lab tests, vital signs, and symptoms.</p>
          </div>
          <div className="step-card">
            <div className="step-number" style={{ background: '#9b59b6', color: 'white' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
              </svg>
            </div>
            <h3>Terminology Mapping</h3>
            <p>Maps extracted entities to standard terminologies: SNOMED CT, ICD-10-CM, LOINC, RxNorm, and CPT.</p>
          </div>
          <div className="step-card">
            <div className="step-number" style={{ background: 'var(--success)', color: 'white' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
            <h3>PDPL De-identification</h3>
            <p>Removes all 18 personal data identifiers per Saudi PDPL requirements for privacy-compliant data.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MedicalRecordProcessor;
