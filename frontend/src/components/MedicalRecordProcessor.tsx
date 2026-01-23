import React, { useState, useEffect } from 'react';

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
  condition: 'bg-red-100 text-red-800 border-red-300',
  diagnosis: 'bg-red-100 text-red-800 border-red-300',
  medication: 'bg-blue-100 text-blue-800 border-blue-300',
  procedure: 'bg-green-100 text-green-800 border-green-300',
  lab_test: 'bg-purple-100 text-purple-800 border-purple-300',
  lab_value: 'bg-purple-100 text-purple-800 border-purple-300',
  vital_sign: 'bg-orange-100 text-orange-800 border-orange-300',
  symptom: 'bg-yellow-100 text-yellow-800 border-yellow-300',
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
  { id: 1, label: 'Extracting text from document', duration: 800 },
  { id: 2, label: 'Running Clinical NLP analysis', duration: 1200 },
  { id: 3, label: 'Mapping to standard terminologies', duration: 1000 },
  { id: 4, label: 'Detecting personal identifiers', duration: 1000 },
  { id: 5, label: 'Applying PDPL de-identification', duration: 1000 },
];

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

  // Simulate processing steps with animation
  const runProcessingAnimation = async () => {
    setShowProcessingOverlay(true);
    setProcessingStep(0);

    for (let i = 0; i < PROCESSING_STEPS.length; i++) {
      setProcessingStep(i + 1);
      await new Promise(resolve => setTimeout(resolve, PROCESSING_STEPS[i].duration));
    }
  };

  const downloadSampleDocument = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/demo/medical-record/download-sample`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'sample_discharge_summary_kfshrc.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download sample document');
    }
  };

  const processDocument = async () => {
    if (!inputText.trim()) {
      setError('Please enter or load a medical document');
      return;
    }

    setLoading(true);
    setError(null);

    // Start the processing animation
    const animationPromise = runProcessingAnimation();

    try {
      const response = await fetch(`${API_BASE}/api/demo/medical-record/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });

      if (!response.ok) {
        throw new Error('Processing failed');
      }

      const data = await response.json();

      // Wait for animation to complete before showing results
      await animationPromise;

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
    setLoading(true);
    setError(null);

    // Start the processing animation
    const animationPromise = runProcessingAnimation();

    try {
      const response = await fetch(`${API_BASE}/api/demo/medical-record/process-sample`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Processing failed');
      }

      const data = await response.json();

      // Wait for animation to complete before showing results
      await animationPromise;

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
            className={`px-1 rounded border ${EntityTypeColors[entity.type] || 'bg-gray-100'}`}
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
            className="bg-red-200 text-red-900 px-1 rounded border border-red-400 line-through"
            title={`${PHITypeLabels[phi.type] || phi.type}: "${phi.text}" -> "${phi.replacement}"`}
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
    <div className="p-6 max-w-7xl mx-auto">
      {/* Processing Overlay */}
      {showProcessingOverlay && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
            <div className="text-center mb-6">
              <div className="w-16 h-16 mx-auto mb-4 relative">
                <div className="absolute inset-0 border-4 border-[#C4A77D]/30 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-[#8B7355] rounded-full border-t-transparent animate-spin"></div>
              </div>
              <h3 className="text-xl font-bold text-[#8B7355]">Processing Document</h3>
              <p className="text-gray-500 text-sm mt-1">PDPL-compliant de-identification in progress</p>
            </div>

            <div className="space-y-3">
              {PROCESSING_STEPS.map((step, index) => {
                const isComplete = processingStep > index + 1 || (processingStep === PROCESSING_STEPS.length && index === PROCESSING_STEPS.length - 1);
                const isActive = processingStep === index + 1;

                return (
                  <div
                    key={step.id}
                    className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${
                      isComplete
                        ? 'bg-green-50 border border-green-200'
                        : isActive
                        ? 'bg-[#FFF8F0] border border-[#C4A77D]'
                        : 'bg-gray-50 border border-gray-200'
                    }`}
                  >
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 ${
                        isComplete
                          ? 'bg-green-500 text-white'
                          : isActive
                          ? 'bg-[#8B7355] text-white'
                          : 'bg-gray-300 text-gray-500'
                      }`}
                    >
                      {isComplete ? (
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <span className="text-xs font-medium">{step.id}</span>
                      )}
                    </div>
                    <span
                      className={`text-sm font-medium ${
                        isComplete ? 'text-green-700' : isActive ? 'text-[#8B7355]' : 'text-gray-500'
                      }`}
                    >
                      {step.label}
                    </span>
                    {isActive && (
                      <div className="ml-auto">
                        <div className="w-4 h-4 border-2 border-[#8B7355] border-t-transparent rounded-full animate-spin"></div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="mt-6 text-center">
              <div className="text-xs text-gray-400">
                Processing time: ~5 seconds
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-[#8B7355] mb-2">Medical Record Processing</h2>
        <p className="text-gray-600">
          Process clinical documents with NLP entity extraction, terminology mapping, and PDPL-compliant de-identification.
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Input Document</h3>
          <div className="flex gap-2">
            <button
              onClick={downloadSampleDocument}
              disabled={loading}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download Sample
            </button>
            <button
              onClick={loadSampleDocument}
              disabled={loading}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
            >
              Load Sample
            </button>
            <button
              onClick={processSampleDocument}
              disabled={loading}
              className="px-4 py-2 text-sm bg-[#C4A77D] hover:bg-[#8B7355] text-white rounded-lg transition-colors"
            >
              Process Sample (KFSHRC)
            </button>
          </div>
        </div>

        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste medical record text here, or click 'Load Sample' to load a KFSHRC discharge summary, or 'Download Sample' to get the sample file..."
          className="w-full h-48 p-3 border border-gray-300 rounded-lg font-mono text-sm resize-y"
        />

        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-gray-500">
            {inputText.length > 0 && (
              <span>{inputText.split(/\s+/).filter(w => w).length} words, {inputText.length} characters</span>
            )}
          </div>
          <button
            onClick={processDocument}
            disabled={loading || !inputText.trim()}
            className="px-6 py-2 bg-[#8B7355] hover:bg-[#6B5344] text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Process Document'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-lg border border-gray-200">
          {/* Stats Bar */}
          <div className="bg-gradient-to-r from-[#8B7355] to-[#C4A77D] text-white p-4 rounded-t-lg">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold">{result.processing_stats.entities_extracted}</div>
                <div className="text-sm opacity-90">Entities Extracted</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{result.processing_stats.phi_detected}</div>
                <div className="text-sm opacity-90">PHI Detected</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{result.processing_stats.terminology_mappings}</div>
                <div className="text-sm opacity-90">Terminology Mappings</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{result.processing_stats.processing_time_seconds.toFixed(2)}s</div>
                <div className="text-sm opacity-90">Processing Time</div>
              </div>
              <div>
                <div className="text-2xl font-bold flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="text-sm opacity-90">PDPL Compliant</div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {[
                { id: 'comparison', label: 'Before/After Comparison' },
                { id: 'entities', label: 'Clinical Entities' },
                { id: 'terminology', label: 'Terminology Mappings' },
                { id: 'phi', label: 'PHI Summary' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-[#8B7355] text-[#8B7355]'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-4">
            {activeTab === 'comparison' && (
              <div>
                <div className="flex items-center gap-4 mb-4">
                  <button
                    onClick={() => setShowOriginal(true)}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      showOriginal ? 'bg-[#8B7355] text-white' : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    Original (with PHI highlighted)
                  </button>
                  <button
                    onClick={() => setShowOriginal(false)}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      !showOriginal ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    De-identified (PDPL)
                  </button>
                </div>

                <div className="bg-gray-50 rounded-lg p-4 max-h-[600px] overflow-y-auto">
                  <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
                    {showOriginal
                      ? highlightPHI(result.original_text, result.phi_detections)
                      : result.deidentified_text}
                  </pre>
                </div>

                {showOriginal && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      <strong>Note:</strong> Highlighted text in red indicates detected Protected Health Information (PHI)
                      that will be removed or replaced during de-identification.
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'entities' && (
              <div>
                <div className="mb-4 flex flex-wrap gap-2">
                  {Object.entries(EntityTypeColors).map(([type, color]) => (
                    <span key={type} className={`px-2 py-1 rounded text-xs ${color} border`}>
                      {type.replace('_', ' ')}
                    </span>
                  ))}
                </div>

                <div className="bg-gray-50 rounded-lg p-4 max-h-[400px] overflow-y-auto mb-4">
                  <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
                    {highlightEntities(result.original_text, result.entities)}
                  </pre>
                </div>

                <h4 className="font-semibold text-gray-800 mb-3">Extracted Entities ({result.entities.length})</h4>
                <div className="grid gap-2 max-h-[300px] overflow-y-auto">
                  {result.entities.map((entity, idx) => (
                    <div key={idx} className={`p-3 rounded-lg border ${EntityTypeColors[entity.type] || 'bg-gray-100'}`}>
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="font-medium">{entity.text}</span>
                          {entity.normalized_term && entity.normalized_term !== entity.text && (
                            <span className="text-gray-600 ml-2">({entity.normalized_term})</span>
                          )}
                        </div>
                        <span className="text-xs uppercase font-medium px-2 py-1 bg-white/50 rounded">
                          {entity.type.replace('_', ' ')}
                        </span>
                      </div>
                      {entity.terminology_code && (
                        <div className="text-sm mt-1 text-gray-600">
                          {entity.terminology_system}: {entity.terminology_code}
                        </div>
                      )}
                      <div className="text-xs text-gray-500 mt-1">
                        Confidence: {(entity.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'terminology' && (
              <div className="grid md:grid-cols-2 gap-6">
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
                    <div key={key} className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                        <span>{icon}</span>
                        {label}
                        <span className="text-sm font-normal text-gray-500">({mappings.length})</span>
                      </h4>
                      <div className="text-xs text-gray-500 mb-2">Mapped to: {system}</div>
                      <div className="space-y-2 max-h-[200px] overflow-y-auto">
                        {mappings.length > 0 ? (
                          mappings.map((mapping, idx) => (
                            <div key={idx} className="bg-white p-2 rounded border border-gray-200">
                              <div className="font-medium text-sm">{mapping.entity_text}</div>
                              {mapping.mappings.map((m, midx) => (
                                <div key={midx} className="text-xs text-gray-600 mt-1">
                                  <span className="font-mono bg-gray-100 px-1 rounded">{m.code}</span>
                                  <span className="ml-2">{m.term || m.name || m.description}</span>
                                  <span className="text-gray-400 ml-1">({m.system})</span>
                                </div>
                              ))}
                            </div>
                          ))
                        ) : (
                          <div className="text-sm text-gray-500 italic">No mappings found</div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {activeTab === 'phi' && (
              <div>
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-semibold text-green-800 mb-2 flex items-center gap-2">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      PDPL Compliance (Saudi Arabia)
                    </h4>
                    <p className="text-sm text-green-700 mb-3">
                      All 18 personal data identifiers are addressed per PDPL (Saudi Personal Data Protection Law) requirements.
                    </p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {result.safe_harbor_18_identifiers.map((id, idx) => (
                        <div key={id} className="flex items-center gap-1 text-green-700">
                          <span className="w-4 h-4 bg-green-200 rounded-full flex items-center justify-center text-green-800">
                            {idx + 1}
                          </span>
                          {PHITypeLabels[id] || id}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h4 className="font-semibold text-red-800 mb-2">
                      PHI Detected: {result.phi_summary.total_phi_found}
                    </h4>
                    <p className="text-sm text-red-700 mb-3">
                      Found {result.phi_summary.types_found.length} types of PHI in this document.
                    </p>
                    <div className="space-y-2">
                      {result.phi_summary.types_found.map((type) => {
                        const items = result.phi_summary.phi_by_type[type] || [];
                        return (
                          <div key={type} className="flex items-center justify-between text-sm">
                            <span className="text-red-700">{PHITypeLabels[type] || type}</span>
                            <span className="bg-red-200 text-red-800 px-2 py-0.5 rounded-full text-xs">
                              {items.length}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                <h4 className="font-semibold text-gray-800 mb-3">Detected PHI Details</h4>
                <div className="bg-gray-50 rounded-lg p-4 max-h-[400px] overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="text-left p-2 font-medium">Type</th>
                        <th className="text-left p-2 font-medium">Original Text</th>
                        <th className="text-left p-2 font-medium">Replacement</th>
                        <th className="text-left p-2 font-medium">Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.phi_detections.map((phi, idx) => (
                        <tr key={idx} className="border-t border-gray-200">
                          <td className="p-2 text-red-700">{PHITypeLabels[phi.type] || phi.type}</td>
                          <td className="p-2 font-mono text-red-600 line-through">{phi.text}</td>
                          <td className="p-2 font-mono text-green-600">{phi.replacement}</td>
                          <td className="p-2">{(phi.confidence * 100).toFixed(0)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Info Cards */}
      {!result && (
        <div className="grid md:grid-cols-3 gap-4 mt-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-2">Clinical NLP</h4>
            <p className="text-sm text-blue-700">
              Extracts medical entities including conditions, medications, procedures, lab tests, vital signs, and symptoms using pattern-based NLP.
            </p>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h4 className="font-semibold text-purple-800 mb-2">Terminology Mapping</h4>
            <p className="text-sm text-purple-700">
              Maps extracted entities to standard terminologies: SNOMED CT, ICD-10-CM, LOINC, RxNorm, and CPT.
            </p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-800 mb-2">PDPL-Compliant De-identification</h4>
            <p className="text-sm text-green-700">
              Removes all 18 personal data identifiers per Saudi PDPL requirements to create research-ready, privacy-compliant data.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MedicalRecordProcessor;
