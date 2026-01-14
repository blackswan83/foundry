import { useState } from 'react';
import { api, PipelineResult, CohortResult, PatientAnalysis } from './services/api';

type TabType = 'pipeline' | 'linkage' | 'deidentification' | 'omop' | 'cohort' | 'ai';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('pipeline');
  const [loading, setLoading] = useState(false);
  const [pipelineResult, setPipelineResult] = useState<PipelineResult | null>(null);
  const [linkageDemo, setLinkageDemo] = useState<Record<string, unknown> | null>(null);
  const [deidDemo, setDeidDemo] = useState<Record<string, unknown> | null>(null);
  const [omopDemo, setOmopDemo] = useState<Record<string, unknown> | null>(null);
  const [cohortQueries, setCohortQueries] = useState<Array<{ id: string; name: string; description: string }>>([]);
  const [selectedQuery, setSelectedQuery] = useState<string>('');
  const [cohortResult, setCohortResult] = useState<CohortResult | null>(null);
  const [analytics, setAnalytics] = useState<Record<string, unknown> | null>(null);
  const [patientAnalysis, setPatientAnalysis] = useState<PatientAnalysis | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<number>(1);
  const [error, setError] = useState<string | null>(null);

  const runPipeline = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.runFullPipeline(30);
      setPipelineResult(result);
      // Load demos after pipeline
      const [linkage, deid, omop, queries, analyticsData] = await Promise.all([
        api.getLinkageDemo(),
        api.getDeidentificationDemo(),
        api.getOMOPTransformationDemo(),
        api.getAvailableQueries(),
        api.getAnalytics(),
      ]);
      setLinkageDemo(linkage);
      setDeidDemo(deid);
      setOmopDemo(omop);
      setCohortQueries(queries.queries);
      setAnalytics(analyticsData);
      if (queries.queries.length > 0) {
        setSelectedQuery(queries.queries[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const runCohortQuery = async () => {
    if (!selectedQuery) return;
    setLoading(true);
    try {
      const result = await api.runCohortQuery(selectedQuery);
      setCohortResult(result.cohort_result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed');
    } finally {
      setLoading(false);
    }
  };

  const analyzePatient = async () => {
    setLoading(true);
    try {
      const result = await api.analyzePatient(selectedPatient);
      setPatientAnalysis(result.analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const resetDemo = async () => {
    await api.resetDemo();
    setPipelineResult(null);
    setLinkageDemo(null);
    setDeidDemo(null);
    setOmopDemo(null);
    setCohortResult(null);
    setPatientAnalysis(null);
    setAnalytics(null);
  };

  const renderPipelineTab = () => (
    <div className="pipeline-section">
      <div className="pipeline-controls">
        <button className="btn btn-primary" onClick={runPipeline} disabled={loading}>
          {loading ? <><span className="loading-spinner"></span> Running...</> : '▶ Run Full Pipeline'}
        </button>
        <button className="btn btn-secondary" onClick={resetDemo}>
          ↺ Reset Demo
        </button>
      </div>

      {error && (
        <div className="result-card" style={{ borderColor: 'var(--danger)' }}>
          <h3>⚠ Error</h3>
          <p>{error}</p>
        </div>
      )}

      <div className="pipeline-steps">
        {[
          { num: 1, title: 'Data Generation', desc: 'Generate synthetic Saudi patient data across multiple hospital systems' },
          { num: 2, title: 'Patient Linkage', desc: 'Tokenize records for cross-system patient linkage' },
          { num: 3, title: 'De-identification', desc: 'Safe Harbor + HiPS compliant PHI removal' },
          { num: 4, title: 'OMOP Transformation', desc: 'Convert to OMOP CDM v5.4 format' },
          { num: 5, title: 'Analytics Ready', desc: 'Enable cohort queries and AI insights' },
        ].map(step => {
          const pipelineStep = pipelineResult?.pipeline_steps?.find(s => s.step === step.num);
          const isCompleted = pipelineStep?.status === 'completed';
          const isActive = loading && pipelineResult?.pipeline_steps?.length === step.num - 1;

          return (
            <div key={step.num} className={`step-card ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`}>
              <div className="step-number">{isCompleted ? '✓' : step.num}</div>
              <h3>{step.title}</h3>
              <p>{step.desc}</p>
            </div>
          );
        })}
      </div>

      {pipelineResult && pipelineResult.overall_status === 'completed' && (
        <div className="result-card">
          <h3>✓ Pipeline Completed Successfully</h3>
          <div className="stats-grid">
            {pipelineResult.pipeline_steps.map(step => (
              <div key={step.step} className="stat-item">
                <div className="value">{
                  typeof step.result === 'object' && step.result !== null
                    ? Object.values(step.result)[0]?.toString() || '✓'
                    : '✓'
                }</div>
                <div className="label">{step.name}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderLinkageTab = () => (
    <div className="results-section">
      <h2>🔗 Cross-System Patient Linkage</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Demonstrates how tokenization enables linking patient records across multiple disconnected hospital systems
        while maintaining complete anonymity.
      </p>

      {linkageDemo ? (
        <>
          <div className="result-card">
            <h3>Scenario: {(linkageDemo as { scenario?: string }).scenario}</h3>
            <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              {(linkageDemo as { explanation?: string }).explanation}
            </p>

            <div className="stats-grid">
              <div className="stat-item">
                <div className="value">{((linkageDemo as { linkage_result?: { records_found?: number } }).linkage_result?.records_found) ?? 0}</div>
                <div className="label">Records Found</div>
              </div>
              <div className="stat-item">
                <div className="value">{((linkageDemo as { linkage_result?: { unique_tokens_generated?: number } }).linkage_result?.unique_tokens_generated) ?? 0}</div>
                <div className="label">Unique Tokens</div>
              </div>
              <div className="stat-item">
                <div className="value" style={{ color: 'var(--success)' }}>
                  {((linkageDemo as { linkage_result?: { successfully_linked?: boolean } }).linkage_result?.successfully_linked) ? '✓ Yes' : 'No'}
                </div>
                <div className="label">Successfully Linked</div>
              </div>
            </div>
          </div>

          <div className="result-card">
            <h3>Patient Records Across Systems</h3>
            <div className="code-block">
              <pre>{JSON.stringify((linkageDemo as { patient_records?: unknown }).patient_records, null, 2)}</pre>
            </div>
          </div>

          <div className="result-card" style={{ borderColor: 'var(--success)' }}>
            <h3>✓ Common Anonymous Token</h3>
            <div style={{ fontSize: '1.5rem', fontFamily: 'monospace', color: 'var(--primary)' }}>
              {((linkageDemo as { linkage_result?: { common_token?: string } }).linkage_result?.common_token) ?? 'N/A'}
            </div>
            <p style={{ marginTop: '0.5rem', color: 'var(--text-secondary)' }}>
              All 4 records share this token, enabling linkage without exposing identity
            </p>
          </div>
        </>
      ) : (
        <div className="result-card">
          <p>Run the pipeline first to see the linkage demonstration.</p>
        </div>
      )}
    </div>
  );

  const renderDeidentificationTab = () => (
    <div className="results-section">
      <h2>🔒 De-identification (Safe Harbor + HiPS)</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Shows Safe Harbor compliant de-identification with realistic surrogate data using the HiPS methodology.
      </p>

      {deidDemo ? (
        <>
          <div className="demo-grid">
            <div className="result-card" style={{ borderColor: 'var(--danger)' }}>
              <h3>⚠ Original PHI (Protected)</h3>
              <div className="code-block">
                <pre>{JSON.stringify(
                  (deidDemo as { before_after?: { original_phi?: unknown } }).before_after?.original_phi,
                  null, 2
                )}</pre>
              </div>
            </div>

            <div className="result-card" style={{ borderColor: 'var(--success)' }}>
              <h3>✓ De-identified Data (Safe)</h3>
              <div className="code-block">
                <pre>{JSON.stringify(
                  (deidDemo as { before_after?: { deidentified?: unknown } }).before_after?.deidentified,
                  null, 2
                )}</pre>
              </div>
            </div>
          </div>

          <div className="result-card">
            <h3>Transformation Summary</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="value" style={{ fontSize: '1.5rem' }}>18</div>
                <div className="label">Identifiers Removed</div>
              </div>
              <div className="stat-item">
                <div className="value" style={{ color: 'var(--success)' }}>✓</div>
                <div className="label">Safe Harbor Compliant</div>
              </div>
              <div className="stat-item">
                <div className="value" style={{ color: 'var(--success)' }}>✓</div>
                <div className="label">Research Utility</div>
              </div>
            </div>
          </div>

          <div className="demo-grid">
            <div className="result-card">
              <h3>PHI Removed</h3>
              <ul style={{ listStyle: 'none' }}>
                {((deidDemo as { before_after?: { phi_removed?: string[] } }).before_after?.phi_removed ?? []).map((item: string, i: number) => (
                  <li key={i} style={{ padding: '0.25rem 0', color: 'var(--danger)' }}>✗ {item}</li>
                ))}
              </ul>
            </div>
            <div className="result-card">
              <h3>Data Preserved</h3>
              <ul style={{ listStyle: 'none' }}>
                {((deidDemo as { before_after?: { data_preserved?: string[] } }).before_after?.data_preserved ?? []).map((item: string, i: number) => (
                  <li key={i} style={{ padding: '0.25rem 0', color: 'var(--success)' }}>✓ {item}</li>
                ))}
              </ul>
            </div>
          </div>
        </>
      ) : (
        <div className="result-card">
          <p>Run the pipeline first to see the de-identification demonstration.</p>
        </div>
      )}
    </div>
  );

  const renderOMOPTab = () => (
    <div className="results-section">
      <h2>🔄 OMOP CDM Transformation</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Demonstrates conversion of heterogeneous clinical data into standardized OMOP Common Data Model v5.4 format.
      </p>

      {omopDemo ? (
        <>
          <div className="result-card">
            <h3>Vocabulary Mappings Applied</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="value">ICD-10</div>
                <div className="label">→ SNOMED</div>
              </div>
              <div className="stat-item">
                <div className="value">Local Labs</div>
                <div className="label">→ LOINC</div>
              </div>
              <div className="stat-item">
                <div className="value">Medications</div>
                <div className="label">→ RxNorm</div>
              </div>
            </div>
          </div>

          <div className="result-card">
            <h3>Sample Transformations</h3>
            <div className="code-block">
              <pre>{JSON.stringify((omopDemo as { transformations?: unknown }).transformations, null, 2)}</pre>
            </div>
          </div>
        </>
      ) : (
        <div className="result-card">
          <p>Run the pipeline first to see the OMOP transformation demonstration.</p>
        </div>
      )}
    </div>
  );

  const renderCohortTab = () => (
    <div className="results-section">
      <h2>📊 Research Cohort Queries</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Query the OMOP-transformed data to build research cohorts based on clinical criteria.
      </p>

      {pipelineResult ? (
        <>
          <div className="pipeline-controls">
            <select
              className="cohort-select"
              value={selectedQuery}
              onChange={(e) => setSelectedQuery(e.target.value)}
            >
              {cohortQueries.map(q => (
                <option key={q.id} value={q.id}>{q.name} - {q.description}</option>
              ))}
            </select>
            <button className="btn btn-primary" onClick={runCohortQuery} disabled={loading}>
              {loading ? <span className="loading-spinner"></span> : 'Run Query'}
            </button>
          </div>

          {cohortResult && (
            <div className="result-card">
              <h3>Cohort: {cohortResult.cohort_name}</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>{cohortResult.description}</p>

              <div className="stats-grid">
                <div className="stat-item">
                  <div className="value">{cohortResult.member_count}</div>
                  <div className="label">Patients</div>
                </div>
                <div className="stat-item">
                  <div className="value">{cohortResult.statistics.demographics.male_percentage}%</div>
                  <div className="label">Male</div>
                </div>
                <div className="stat-item">
                  <div className="value">{cohortResult.statistics.demographics.age_mean}</div>
                  <div className="label">Mean Age</div>
                </div>
                <div className="stat-item">
                  <div className="value">{cohortResult.statistics.clinical.visits_per_person}</div>
                  <div className="label">Avg Visits</div>
                </div>
              </div>
            </div>
          )}

          {analytics && (
            <div className="result-card">
              <h3>Data Analytics Summary</h3>
              <div className="code-block">
                <pre>{JSON.stringify((analytics as { data_summary?: unknown }).data_summary, null, 2)}</pre>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="result-card">
          <p>Run the pipeline first to enable cohort queries.</p>
        </div>
      )}
    </div>
  );

  const renderAITab = () => (
    <div className="results-section">
      <h2>🤖 AI Clinical Intelligence</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        AI-powered analysis of patient encounters generating actionable clinical insights.
      </p>

      {pipelineResult ? (
        <>
          <div className="pipeline-controls">
            <input
              type="number"
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(parseInt(e.target.value) || 1)}
              min={1}
              max={30}
              style={{
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                width: '120px',
              }}
            />
            <button className="btn btn-primary" onClick={analyzePatient} disabled={loading}>
              {loading ? <span className="loading-spinner"></span> : 'Analyze Patient'}
            </button>
          </div>

          {patientAnalysis && (
            <>
              <div className="result-card">
                <h3>Patient Summary</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="value">{patientAnalysis.summary.demographics.age}</div>
                    <div className="label">Age</div>
                  </div>
                  <div className="stat-item">
                    <div className="value">{patientAnalysis.summary.demographics.gender}</div>
                    <div className="label">Gender</div>
                  </div>
                  <div className="stat-item">
                    <div className="value">{patientAnalysis.summary.clinical_summary.total_visits}</div>
                    <div className="label">Visits</div>
                  </div>
                  <div className="stat-item">
                    <div className="value" style={{
                      color: patientAnalysis.risk_score.color === 'red' ? 'var(--danger)' :
                             patientAnalysis.risk_score.color === 'orange' ? 'var(--warning)' :
                             patientAnalysis.risk_score.color === 'yellow' ? 'var(--warning)' : 'var(--success)'
                    }}>
                      {patientAnalysis.risk_score.level}
                    </div>
                    <div className="label">Risk Level</div>
                  </div>
                </div>
              </div>

              <div className="result-card">
                <h3>AI-Generated Insights ({patientAnalysis.insights.length})</h3>
                {patientAnalysis.insights.length > 0 ? (
                  patientAnalysis.insights.map((insight, i) => (
                    <div key={i} className={`insight-card ${insight.severity}`}>
                      <div className="insight-title">
                        {insight.severity === 'high' ? '🔴' :
                         insight.severity === 'medium' ? '🟠' :
                         insight.severity === 'low' ? '🔵' : '🟢'} {insight.title}
                      </div>
                      <div className="insight-description">{insight.description}</div>
                      {insight.recommendations.length > 0 && (
                        <div style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}>
                          <strong>Recommendations:</strong>
                          <ul style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                            {insight.recommendations.slice(0, 2).map((rec, j) => (
                              <li key={j}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p style={{ color: 'var(--text-muted)' }}>No significant findings for this patient.</p>
                )}
              </div>

              <div className="result-card">
                <h3>Risk Score Breakdown</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="value" style={{ color: 'var(--danger)' }}>
                      {patientAnalysis.risk_score.breakdown.high_severity_findings}
                    </div>
                    <div className="label">High Severity</div>
                  </div>
                  <div className="stat-item">
                    <div className="value" style={{ color: 'var(--warning)' }}>
                      {patientAnalysis.risk_score.breakdown.medium_severity_findings}
                    </div>
                    <div className="label">Medium Severity</div>
                  </div>
                  <div className="stat-item">
                    <div className="value" style={{ color: 'var(--info)' }}>
                      {patientAnalysis.risk_score.breakdown.low_severity_findings}
                    </div>
                    <div className="label">Low Severity</div>
                  </div>
                </div>
              </div>
            </>
          )}
        </>
      ) : (
        <div className="result-card">
          <p>Run the pipeline first to enable AI analysis.</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="container">
      <header className="header">
        <h1>Nuraxi Foundry</h1>
        <p className="subtitle">King Faisal Specialist Hospital & Research Centre</p>
        <p className="version">Demo Prototype v1.0 | January 2026</p>
      </header>

      <div className="tabs">
        <button className={`tab ${activeTab === 'pipeline' ? 'active' : ''}`} onClick={() => setActiveTab('pipeline')}>
          Pipeline
        </button>
        <button className={`tab ${activeTab === 'linkage' ? 'active' : ''}`} onClick={() => setActiveTab('linkage')}>
          Patient Linkage
        </button>
        <button className={`tab ${activeTab === 'deidentification' ? 'active' : ''}`} onClick={() => setActiveTab('deidentification')}>
          De-identification
        </button>
        <button className={`tab ${activeTab === 'omop' ? 'active' : ''}`} onClick={() => setActiveTab('omop')}>
          OMOP Transform
        </button>
        <button className={`tab ${activeTab === 'cohort' ? 'active' : ''}`} onClick={() => setActiveTab('cohort')}>
          Cohort Queries
        </button>
        <button className={`tab ${activeTab === 'ai' ? 'active' : ''}`} onClick={() => setActiveTab('ai')}>
          AI Insights
        </button>
      </div>

      {activeTab === 'pipeline' && renderPipelineTab()}
      {activeTab === 'linkage' && renderLinkageTab()}
      {activeTab === 'deidentification' && renderDeidentificationTab()}
      {activeTab === 'omop' && renderOMOPTab()}
      {activeTab === 'cohort' && renderCohortTab()}
      {activeTab === 'ai' && renderAITab()}
    </div>
  );
}

export default App;
