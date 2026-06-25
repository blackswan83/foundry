import { useState, useEffect, useRef } from 'react';
import { api, ExtractionSample, ExtractionResult, ExtractedEntity } from '../services/api';

// Map entity type -> CSS class for the inline color coding
const ENTITY_CLASS: Record<string, string> = {
  condition: 'ent-condition',
  morphology: 'ent-morphology',
  procedure: 'ent-procedure',
  medication: 'ent-medication',
  lab: 'ent-lab',
  anatomical_site: 'ent-anatomy',
  gene: 'ent-gene',
  variant: 'ent-variant',
  biomarker: 'ent-biomarker',
};

const LEGEND: Array<{ key: string; label: string; layer: string }> = [
  { key: 'condition', label: 'Condition / Disorder', layer: 'clinical' },
  { key: 'morphology', label: 'Finding / Morphology', layer: 'clinical' },
  { key: 'procedure', label: 'Procedure', layer: 'clinical' },
  { key: 'medication', label: 'Medication', layer: 'clinical' },
  { key: 'lab', label: 'Lab / Assay', layer: 'clinical' },
  { key: 'anatomical_site', label: 'Anatomical Site', layer: 'clinical' },
  { key: 'gene', label: 'Gene (HGNC)', layer: 'molecular' },
  { key: 'variant', label: 'Variant (HGVS)', layer: 'molecular' },
  { key: 'biomarker', label: 'Biomarker', layer: 'molecular' },
];

function triggerDownload(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function csvEscape(v: string | number | boolean): string {
  const s = String(v).replace(/\n/g, ' ').trim();
  return /[",]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export default function ClinicalTextExtraction() {
  const [samples, setSamples] = useState<ExtractionSample[]>([]);
  const [selectedSample, setSelectedSample] = useState<string>('molecular_pathology');
  const [text, setText] = useState<string>('');
  const [threshold, setThreshold] = useState<number>(0.5);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hover, setHover] = useState<{ ent: ExtractedEntity; x: number; y: number } | null>(null);
  const [view, setView] = useState<'annotated' | 'table'>('annotated');
  const textRef = useRef(text);
  textRef.current = text;

  useEffect(() => {
    api.getExtractionSamples().then((r) => setSamples(r.samples)).catch(() => {});
    loadSample('molecular_pathology');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadSample = async (id: string) => {
    setSelectedSample(id);
    setResult(null);
    setError(null);
    if (id === '__paste') {
      setText('');
      return;
    }
    try {
      const r = await api.getExtractionSample(id);
      setText(r.text);
    } catch {
      setError('Could not load the sample note.');
    }
  };

  const runExtract = async (th: number = threshold) => {
    const current = textRef.current;
    if (!current.trim()) {
      setError('Load a sample or paste a clinical note first.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const r = await api.runExtraction(current, th);
      setResult(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Extraction failed');
    } finally {
      setLoading(false);
    }
  };

  // Re-run when the threshold is committed (slider release / keyboard) if we
  // already have a result, so the confidence filter is visibly adjustable.
  const commitThreshold = () => {
    if (result) runExtract(threshold);
  };

  // ---- exports ----
  const exportCSV = () => {
    if (!result) return;
    const header = ['span_text', 'entity_type', 'layer', 'vocabulary', 'concept', 'code', 'confidence', 'negated', 'historical', 'subject', 'context'];
    const rows = result.entities.map((e) => [
      e.text, e.entity_type_label, e.layer, e.vocabulary, e.concept, e.code,
      e.confidence, e.negated ? 'yes' : 'no', e.historical ? 'yes' : 'no', e.subject, e.context,
    ].map(csvEscape).join(','));
    triggerDownload([header.join(','), ...rows].join('\n'), 'elembic_extracted_entities.csv', 'text/csv');
  };

  const exportJSON = () => {
    if (!result) return;
    const payload = {
      source_note: text,
      generated: 'Elembic Clinical Text Extraction (synthetic demo; codes illustrative)',
      stats: result.stats,
      vocabularies_used: result.vocabularies_used,
      operations: result.operations,
      entities: result.entities,
    };
    triggerDownload(JSON.stringify(payload, null, 2), 'elembic_extracted_entities.json', 'application/json');
  };

  const exportHTML = () => {
    if (!result) return;
    let cursor = 0;
    let body = '';
    const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    result.entities.forEach((e) => {
      if (e.start > cursor) body += esc(text.slice(cursor, e.start));
      const deco = `${e.negated ? 'text-decoration:line-through;' : ''}${e.historical ? 'font-style:italic;' : ''}`;
      body += `<span style="background:${e.color}22;border:1px solid ${e.color}66;border-radius:3px;padding:0 2px;${deco}" title="${esc(e.concept)} [${e.vocabulary} ${e.code}] conf=${e.confidence}">${esc(text.slice(e.start, e.end))}</span>`;
      cursor = e.end;
    });
    if (cursor < text.length) body += esc(text.slice(cursor));
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>Elembic annotated note</title></head><body style="font-family:monospace;white-space:pre-wrap;line-height:1.8;padding:24px;max-width:900px;margin:auto"><h3>Elembic — Annotated Clinical Note (synthetic; codes illustrative)</h3>${body}</body></html>`;
    triggerDownload(html, 'elembic_annotated_note.html', 'text/html');
  };

  const exportOps = () => {
    if (!result) return;
    const lines = [
      'ELEMBIC — CLINICAL TEXT EXTRACTION — OPERATIONS / AUDIT LOG',
      'Synthetic input. Codes are illustrative and pending terminology-server validation.',
      `Threshold: ${result.stats.threshold}`,
      '',
      ...result.operations.map((o) => `[${o.step}] ${o.operation}\n      ${o.detail}  (count: ${o.count})`),
      '',
      'Vocabularies used: ' + result.vocabularies_used.join(', '),
    ];
    triggerDownload(lines.join('\n'), 'elembic_operations_log.txt', 'text/plain');
  };

  // ---- annotated rendering ----
  const renderAnnotated = () => {
    if (!result) {
      return <div className="annotated-text muted">Run extraction to see inline SNOMED / genomic annotations.</div>;
    }
    const parts: JSX.Element[] = [];
    let cursor = 0;
    result.entities.forEach((e, i) => {
      if (e.start > cursor) parts.push(<span key={`t${i}`}>{text.slice(cursor, e.start)}</span>);
      const cls = ENTITY_CLASS[e.entity_type] || '';
      const flags = `${e.negated ? ' ent-negated' : ''}${e.historical ? ' ent-historical' : ''}`;
      parts.push(
        <span
          key={`e${i}`}
          className={`ent ${cls}${flags}`}
          onMouseEnter={(ev) => setHover({ ent: e, x: ev.clientX, y: ev.clientY })}
          onMouseMove={(ev) => setHover({ ent: e, x: ev.clientX, y: ev.clientY })}
          onMouseLeave={() => setHover(null)}
        >
          {text.slice(e.start, e.end)}
        </span>
      );
      cursor = e.end;
    });
    if (cursor < text.length) parts.push(<span key="tail">{text.slice(cursor)}</span>);
    return <div className="annotated-text">{parts}</div>;
  };

  const stat = (k: string) => (result ? result.stats[k] ?? 0 : 0);

  return (
    <div className="results-section extraction-tab">
      <h2>Clinical Text Extraction &amp; SNOMED Annotation</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
        The Elembic NER + entity-linking layer turns <strong>unstructured</strong> clinical and molecular-pathology
        text into structured, coded entities — SNOMED CT for the clinical layer; HGNC / HGVS / ClinVar / LOINC for the
        molecular layer — with explicit operations at every step.
      </p>

      <div className="extraction-banner">
        <span>🧪 Synthetic input only — no real PHI.</span>
        <span>🔖 Codes are <strong>illustrative</strong> (MedCAT / MetaCAT-style demo) and must be validated against a live terminology server before the call.</span>
      </div>

      {/* Controls */}
      <div className="extraction-controls">
        <div className="control-group">
          <label>Sample note</label>
          <select
            className="cohort-select"
            value={selectedSample}
            onChange={(e) => loadSample(e.target.value)}
          >
            {samples.length === 0 && <option value={selectedSample}>Loading…</option>}
            {samples.map((s) => (
              <option key={s.id} value={s.id}>{s.title}</option>
            ))}
            <option value="__paste">Paste your own (Demo Mode)…</option>
          </select>
        </div>
        <div className="control-group threshold-group">
          <label>Confidence threshold: <strong>{threshold.toFixed(2)}</strong></label>
          <input
            type="range" min={0} max={0.99} step={0.01} value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            onMouseUp={commitThreshold}
            onTouchEnd={commitThreshold}
            onKeyUp={commitThreshold}
          />
        </div>
        <button className="btn btn-primary" onClick={() => runExtract()} disabled={loading}>
          {loading ? <><span className="loading-spinner" /> Extracting…</> : 'Extract & Annotate'}
        </button>
      </div>

      {error && (
        <div className="result-card" style={{ borderLeft: '4px solid var(--danger)' }}>
          <p style={{ color: 'var(--danger)' }}>{error}</p>
        </div>
      )}

      {result && (
        <div className="stats-bar extraction-stats">
          <div className="stat-item"><div className="value">{stat('entities_passed_threshold')}</div><div className="label">Entities Linked</div></div>
          <div className="stat-item"><div className="value">{stat('clinical_layer')}</div><div className="label">SNOMED Clinical</div></div>
          <div className="stat-item"><div className="value">{stat('molecular_layer')}</div><div className="label">Molecular (HGNC/HGVS)</div></div>
          <div className="stat-item"><div className="value">{stat('negated_entities')}</div><div className="label">Negated</div></div>
          <div className="stat-item"><div className="value">{stat('historical_entities') + stat('family_entities')}</div><div className="label">Context-flagged</div></div>
        </div>
      )}

      {/* Three panels */}
      <div className="extraction-panels">
        {/* Left: raw input */}
        <div className="result-card panel">
          <h3>1 · Raw clinical note</h3>
          <textarea
            className="document-input extraction-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste a clinical or molecular-pathology note here, or pick a sample above…"
          />
          <div className="panel-foot">{text.trim() ? text.trim().split(/\s+/).length : 0} words</div>
        </div>

        {/* Center: annotated text */}
        <div className="result-card panel">
          <h3>2 · Annotated text</h3>
          {renderAnnotated()}
        </div>

        {/* Right: structured output */}
        <div className="result-card panel">
          <div className="result-tabs" style={{ marginBottom: '0.75rem' }}>
            <button className={`result-tab ${view === 'annotated' ? 'active' : ''}`} onClick={() => setView('annotated')}>Entity table</button>
            <button className={`result-tab ${view === 'table' ? 'active' : ''}`} onClick={() => setView('table')}>Operations</button>
          </div>
          {view === 'annotated' ? (
            <div className="phi-table-container extraction-table">
              <table className="phi-table">
                <thead>
                  <tr>
                    <th>Span</th><th>Type</th><th>Concept</th><th>Code</th><th>Conf.</th><th>Flags</th>
                  </tr>
                </thead>
                <tbody>
                  {result?.entities.map((e, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600 }}>{e.text}</td>
                      <td><span className={`ent-chip ${ENTITY_CLASS[e.entity_type]}`}>{e.entity_type_label}</span></td>
                      <td>{e.concept}</td>
                      <td><code>{e.vocabulary} {e.code}</code></td>
                      <td>{e.confidence.toFixed(2)}</td>
                      <td className="flag-cell">
                        {e.negated && <span className="flag neg">neg</span>}
                        {e.historical && <span className="flag hist">hist</span>}
                        {e.subject === 'family' && <span className="flag fam">family</span>}
                      </td>
                    </tr>
                  ))}
                  {!result && <tr><td colSpan={6} className="muted">No entities yet.</td></tr>}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="operations-list">
              {result?.operations.map((o) => (
                <div className="operation-row" key={o.step}>
                  <span className="op-step">{o.step}</span>
                  <div>
                    <div className="op-name">{o.operation}</div>
                    <div className="op-detail">{o.detail}</div>
                  </div>
                  <span className="op-count">{o.count}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="result-card">
        <h3>Entity legend</h3>
        <div className="entity-legend">
          {LEGEND.map((l) => (
            <span key={l.key} className={`ent ${ENTITY_CLASS[l.key]}`} style={{ fontSize: '0.72rem' }}>
              {l.label} <span style={{ opacity: 0.6 }}>· {l.layer}</span>
            </span>
          ))}
          <span className="ent ent-negated" style={{ fontSize: '0.72rem' }}>negated (struck through)</span>
          <span className="ent ent-historical" style={{ fontSize: '0.72rem' }}>historical (italic)</span>
        </div>
      </div>

      {/* Operations performed (audit) */}
      {result && (
        <div className="result-card">
          <h3>Operations performed (audit trail)</h3>
          <div className="operations-list">
            {result.operations.map((o) => (
              <div className="operation-row" key={`op${o.step}`}>
                <span className="op-step">{o.step}</span>
                <div>
                  <div className="op-name">{o.operation}</div>
                  <div className="op-detail">{o.detail}</div>
                </div>
                <span className="op-count">{o.count}</span>
              </div>
            ))}
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.75rem' }}>
            These extracted, coded entities flow into the existing pipeline:
            <strong> De-identification → Patient Linkage → OMOP → Cohort / Insights</strong>.
          </p>
        </div>
      )}

      {/* Exports */}
      {result && (
        <div className="result-card">
          <h3>Export</h3>
          <div className="pipeline-controls" style={{ marginBottom: 0 }}>
            <button className="btn btn-primary" onClick={exportCSV}>Download CSV</button>
            <button className="btn btn-secondary" onClick={exportJSON}>Download JSON</button>
            <button className="btn btn-secondary" onClick={exportHTML}>Annotated HTML</button>
            <button className="btn btn-secondary" onClick={exportOps}>Operations log</button>
          </div>
        </div>
      )}

      {/* Hover tooltip */}
      {hover && (
        <div
          className="entity-tooltip"
          style={{ left: Math.min(hover.x + 14, window.innerWidth - 280), top: hover.y + 14 }}
        >
          <div className="tt-concept">{hover.ent.concept}</div>
          <div className="tt-row"><span>Vocabulary</span><strong>{hover.ent.vocabulary}</strong></div>
          <div className="tt-row"><span>Code</span><code>{hover.ent.code}</code></div>
          <div className="tt-row"><span>Type</span>{hover.ent.entity_type_label}</div>
          <div className="tt-row"><span>Confidence</span><strong>{hover.ent.confidence.toFixed(2)}</strong></div>
          <div className="tt-row">
            <span>Context</span>
            {[
              hover.ent.negated ? 'negated' : 'affirmed',
              hover.ent.historical ? 'historical' : 'current',
              hover.ent.subject,
            ].join(' · ')}
          </div>
          {hover.ent.note && <div className="tt-note">{hover.ent.note}</div>}
        </div>
      )}
    </div>
  );
}
