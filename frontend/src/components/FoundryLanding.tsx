import React from 'react';

// Nuraxi Brand Colors
const colors = {
  primary: '#8B7355',
  secondary: '#6B5B4F',
  accent: '#C4A77D',
  background: '#E8E4DC',
  backgroundGradient: 'linear-gradient(135deg, #E8E4DC 0%, #D4CFC4 100%)',
  text: '#3D3D3D',
  textLight: '#6B6B6B',
  white: '#FFFFFF',
  success: '#4A7C59',
  warning: '#D4A574',
  cyan: '#00A0B0',
};

// Section 1: THE PROBLEM (Attention)
const Section1_TheProblem = () => (
  <div style={{
    minHeight: '80vh',
    background: colors.backgroundGradient,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  }}>
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: colors.textLight,
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      The Challenge
    </div>

    <h1 style={{
      fontSize: '42px',
      fontWeight: '300',
      color: colors.primary,
      textAlign: 'center',
      marginBottom: '40px',
      maxWidth: '900px',
      lineHeight: 1.2,
    }}>
      Your clinical data is <span style={{ fontWeight: '600' }}>fragmented</span>,
      <span style={{ fontWeight: '600' }}> siloed</span>, and
      <span style={{ fontWeight: '600' }}> locked away</span>
    </h1>

    <div style={{
      display: 'flex',
      gap: '24px',
      marginBottom: '50px',
      flexWrap: 'wrap',
      justifyContent: 'center',
    }}>
      {['EHR System', 'Lab Results', 'Clinical Notes', 'Imaging Reports'].map((silo, i) => (
        <div key={i} style={{
          width: '120px',
          height: '120px',
          background: 'rgba(255,255,255,0.6)',
          borderRadius: '12px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          transform: `rotate(${(i - 1.5) * 5}deg)`,
          border: '2px dashed rgba(139, 115, 85, 0.3)',
        }}>
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke={colors.primary} strokeWidth="1.5">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path d="M21 5v4c0 1.66-4 3-9 3s-9-1.34-9-3V5"/>
            <path d="M21 9v4c0 1.66-4 3-9 3s-9-1.34-9-3V9"/>
            <path d="M21 13v4c0 1.66-4 3-9 3s-9-1.34-9-3v-4"/>
          </svg>
          <span style={{ fontSize: '12px', color: colors.text, marginTop: '10px', textAlign: 'center' }}>
            {silo}
          </span>
        </div>
      ))}
    </div>

    <div style={{
      display: 'flex',
      gap: '50px',
      marginTop: '20px',
      flexWrap: 'wrap',
      justifyContent: 'center',
    }}>
      {[
        { stat: '80%', label: 'of clinical data is unstructured' },
        { stat: '0%', label: 'AI-ready without transformation' },
        { stat: '∞', label: 'value locked inside' },
      ].map((item, i) => (
        <div key={i} style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '38px', fontWeight: '600', color: colors.primary }}>{item.stat}</div>
          <div style={{ fontSize: '13px', color: colors.textLight, maxWidth: '140px' }}>{item.label}</div>
        </div>
      ))}
    </div>
  </div>
);

// Section 2: WHAT IS THE FOUNDRY (Interest)
const Section2_WhatIsFoundry = () => (
  <div style={{
    minHeight: '80vh',
    background: colors.white,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  }}>
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: colors.textLight,
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      The Solution
    </div>

    <div style={{
      fontSize: '24px',
      color: colors.primary,
      marginBottom: '10px',
      fontWeight: '300',
      letterSpacing: '4px',
    }}>
      NURAXI
    </div>

    <h2 style={{
      fontSize: '46px',
      fontWeight: '300',
      color: colors.primary,
      textAlign: 'center',
      marginBottom: '20px',
    }}>
      The <span style={{ fontWeight: '600' }}>Foundry</span>
    </h2>

    <p style={{
      fontSize: '20px',
      color: colors.textLight,
      textAlign: 'center',
      maxWidth: '700px',
      marginBottom: '50px',
      lineHeight: 1.6,
    }}>
      A sovereign data transformation engine that converts fragmented clinical data
      into an AI-ready, research-grade intelligence platform
    </p>

    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '30px',
      marginBottom: '40px',
      flexWrap: 'wrap',
      justifyContent: 'center',
    }}>
      {/* Before */}
      <div style={{
        width: '180px',
        height: '110px',
        background: '#F5F0EB',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        border: '2px dashed rgba(139, 115, 85, 0.3)',
      }}>
        <div style={{ fontSize: '13px', color: colors.textLight, marginBottom: '8px' }}>Raw Clinical Data</div>
        <div style={{ display: 'flex', gap: '6px' }}>
          {[1,2,3,4].map(i => (
            <div key={i} style={{
              width: '26px', height: '32px',
              background: 'rgba(139, 115, 85, 0.2)',
              borderRadius: '4px',
              transform: `rotate(${(i-2) * 8}deg)`,
            }} />
          ))}
        </div>
      </div>

      {/* Arrow with Foundry */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{
          background: colors.primary,
          color: colors.white,
          padding: '10px 20px',
          borderRadius: '30px',
          fontSize: '13px',
          fontWeight: '500',
          marginBottom: '8px',
        }}>
          The Foundry
        </div>
        <span style={{ fontSize: '24px', color: colors.primary }}>→</span>
      </div>

      {/* After */}
      <div style={{
        width: '180px',
        height: '110px',
        background: 'linear-gradient(135deg, #F0F7F4 0%, #E8F4F0 100%)',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        border: '2px solid rgba(74, 124, 89, 0.3)',
      }}>
        <div style={{ fontSize: '13px', color: colors.success, marginBottom: '8px' }}>OMOP Structured Data</div>
        <div style={{ display: 'flex', gap: '6px' }}>
          {[1,2,3,4].map(i => (
            <div key={i} style={{
              width: '26px', height: '32px',
              background: colors.success,
              borderRadius: '4px',
              opacity: 0.6,
            }} />
          ))}
        </div>
      </div>
    </div>

    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '12px 24px',
      background: '#F5F5F5',
      borderRadius: '8px',
    }}>
      <span style={{ fontSize: '13px', color: colors.textLight }}>Powered by</span>
      <span style={{ fontSize: '15px', fontWeight: '600', color: colors.text }}>OMOP Common Data Model</span>
      <span style={{ fontSize: '11px', color: colors.textLight }}>• Global Standard</span>
    </div>
  </div>
);

// Section 3: HOW IT WORKS (Interest)
const Section3_HowItWorks = () => (
  <div style={{
    minHeight: '60vh',
    background: colors.backgroundGradient,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  }}>
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: colors.textLight,
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      The Process
    </div>

    <h2 style={{
      fontSize: '36px',
      fontWeight: '300',
      color: colors.primary,
      marginBottom: '40px',
    }}>
      How <span style={{ fontWeight: '600' }}>The Foundry</span> Works
    </h2>

    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '12px',
      maxWidth: '1100px',
      flexWrap: 'wrap',
      justifyContent: 'center',
    }}>
      {[
        { icon: '📥', title: '1. Ingest', desc: 'Connect to EHRs, Labs, Clinical Notes, FHIR feeds' },
        { icon: '🔒', title: '2. De-identify', desc: 'Safe Harbor compliant removal of all PII' },
        { icon: '🔗', title: '3. Tokenize', desc: 'Anonymous linkage across multiple data sources' },
        { icon: '🏷️', title: '4. Encode', desc: 'Medical coding: ICD-10, SNOMED-CT, LOINC, RxNorm' },
        { icon: '✓', title: '5. OMOP Output', desc: 'Structured, queryable, AI-ready data', isLast: true },
      ].map((step, i) => (
        <React.Fragment key={i}>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '150px',
          }}>
            <div style={{
              width: '70px',
              height: '70px',
              background: step.isLast ? colors.success : colors.white,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
              marginBottom: '14px',
            }}>
              <span style={{ fontSize: '28px' }}>{step.icon}</span>
            </div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: step.isLast ? colors.success : colors.primary, marginBottom: '6px' }}>{step.title}</div>
            <div style={{ fontSize: '12px', color: colors.textLight, textAlign: 'center', lineHeight: 1.4 }}>
              {step.desc}
            </div>
          </div>
          {i < 4 && <div style={{ paddingTop: '30px', color: colors.primary, fontSize: '20px' }}>→</div>}
        </React.Fragment>
      ))}
    </div>

    <div style={{
      marginTop: '40px',
      padding: '16px 32px',
      background: 'rgba(255,255,255,0.7)',
      borderRadius: '12px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
    }}>
      <span style={{ fontSize: '18px' }}>🛡️</span>
      <span style={{ fontSize: '14px', color: colors.text }}>
        All processing happens <strong>locally</strong> within your sovereign infrastructure
      </span>
    </div>
  </div>
);

// Section 4: FOUR PILLARS OF TRUST (Desire)
const Section4_CorePillars = () => (
  <div style={{
    minHeight: '70vh',
    background: colors.white,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  }}>
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: colors.textLight,
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      Core Principles
    </div>

    <h2 style={{
      fontSize: '36px',
      fontWeight: '300',
      color: colors.primary,
      marginBottom: '40px',
    }}>
      Four Pillars of <span style={{ fontWeight: '600' }}>Trust</span>
    </h2>

    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: '24px',
      maxWidth: '900px',
      width: '100%',
    }}>
      {[
        {
          icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><circle cx="12" cy="8" r="4"/><path d="M4 20v-2a6 6 0 0112 0v2"/><line x1="4" y1="6" x2="20" y2="20"/></svg>,
          title: 'De-identified',
          desc: 'Safe Harbor compliant de-identification removes all 18 HIPAA identifiers. No patient information ever leaves your control.',
          color: colors.primary,
          bg: 'linear-gradient(135deg, #FDF8F3 0%, #F5EDE4 100%)',
        },
        {
          icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>,
          title: 'Tokenized',
          desc: 'Anonymous patient tokens enable longitudinal tracking across multiple data sources without exposing identity.',
          color: '#4A7C9B',
          bg: 'linear-gradient(135deg, #F3F8FD 0%, #E4EDF5 100%)',
        },
        {
          icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><path d="M9 12h6"/><path d="M9 16h6"/></svg>,
          title: 'Medical Coding',
          desc: 'Standardized terminology using ICD-10, SNOMED-CT, LOINC, and RxNorm makes data computable and interoperable.',
          color: colors.success,
          bg: 'linear-gradient(135deg, #F3FDF8 0%, #E4F5ED 100%)',
        },
        {
          icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>,
          title: 'Sovereign',
          desc: 'Data never leaves your infrastructure. Full control, full compliance, full sovereignty.',
          color: '#9B4A7C',
          bg: 'linear-gradient(135deg, #FDF3F8 0%, #F5E4ED 100%)',
        },
      ].map((pillar, i) => (
        <div key={i} style={{
          padding: '32px',
          background: pillar.bg,
          borderRadius: '16px',
          borderLeft: `4px solid ${pillar.color}`,
        }}>
          <div style={{
            width: '54px',
            height: '54px',
            background: pillar.color,
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '16px',
          }}>
            {pillar.icon}
          </div>
          <h3 style={{ fontSize: '20px', fontWeight: '600', color: pillar.color, marginBottom: '10px' }}>
            {pillar.title}
          </h3>
          <p style={{ fontSize: '14px', color: colors.textLight, lineHeight: 1.6, margin: 0 }}>
            {pillar.desc}
          </p>
        </div>
      ))}
    </div>
  </div>
);

// Section 5: WHAT YOU CAN ACHIEVE (Desire)
const Section5_Outcomes = () => (
  <div style={{
    minHeight: '50vh',
    background: colors.backgroundGradient,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  }}>
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: colors.textLight,
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      Capabilities
    </div>

    <h2 style={{
      fontSize: '36px',
      fontWeight: '300',
      color: colors.primary,
      marginBottom: '40px',
    }}>
      What You Can <span style={{ fontWeight: '600' }}>Achieve</span>
    </h2>

    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '20px',
      maxWidth: '950px',
      width: '100%',
    }}>
      {[
        { icon: '📊', title: 'Analytics', desc: 'Longitudinal analysis across conditions, departments, outcomes' },
        { icon: '🔬', title: 'Research', desc: 'Deep clinical research from connected, structured datasets' },
        { icon: '🤖', title: 'AI Training', desc: 'Train AI agents and models on de-identified clinical data' },
        { icon: '🤝', title: 'Data Sharing', desc: 'Controlled third-party access to de-identified OMOP data' },
      ].map((item, i) => (
        <div key={i} style={{
          padding: '28px',
          background: colors.white,
          borderRadius: '16px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
          textAlign: 'center',
        }}>
          <div style={{
            width: '60px',
            height: '60px',
            background: 'linear-gradient(135deg, #E8E4DC 0%, #D4CFC4 100%)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
          }}>
            <span style={{ fontSize: '28px' }}>{item.icon}</span>
          </div>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: colors.primary, marginBottom: '10px' }}>
            {item.title}
          </h3>
          <p style={{ fontSize: '13px', color: colors.textLight, lineHeight: 1.5, margin: 0 }}>
            {item.desc}
          </p>
        </div>
      ))}
    </div>

    <div style={{
      marginTop: '40px',
      display: 'flex',
      gap: '32px',
      alignItems: 'center',
      flexWrap: 'wrap',
      justifyContent: 'center',
    }}>
      {['PDPL Compliant', 'HIPAA Safe Harbor', 'OMOP Standard'].map((item, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '16px', color: colors.success }}>✓</span>
          <span style={{ fontSize: '14px', color: colors.text }}>{item}</span>
        </div>
      ))}
    </div>
  </div>
);

// Section 6: CLINICAL INTELLIGENCE (Desire)
const Section6_ClinicalIntelligence = () => (
  <div style={{
    minHeight: '60vh',
    background: 'linear-gradient(135deg, #2D2D2D 0%, #1A1A1A 100%)',
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  }}>
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: 'rgba(255,255,255,0.5)',
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      AI Powered
    </div>

    <h2 style={{
      fontSize: '36px',
      fontWeight: '300',
      color: colors.white,
      marginBottom: '16px',
    }}>
      Clinical <span style={{ fontWeight: '600', color: colors.accent }}>Intelligence</span>
    </h2>

    <p style={{
      fontSize: '16px',
      color: 'rgba(255,255,255,0.7)',
      textAlign: 'center',
      maxWidth: '600px',
      marginBottom: '40px',
    }}>
      The Foundry unlocks AI and agentic power for immediate clinical and commercial impact
    </p>

    <div style={{
      display: 'flex',
      gap: '30px',
      maxWidth: '850px',
      flexWrap: 'wrap',
      justifyContent: 'center',
    }}>
      {/* Vitruvia Card */}
      <div style={{
        flex: '1 1 350px',
        padding: '32px',
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '20px',
        border: '1px solid rgba(255,255,255,0.1)',
      }}>
        <div style={{
          width: '50px',
          height: '4px',
          background: colors.accent,
          borderRadius: '2px',
          marginBottom: '16px',
        }} />
        <h3 style={{ fontSize: '24px', fontWeight: '600', color: colors.white, marginBottom: '12px' }}>
          Vitruvia
        </h3>
        <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)', lineHeight: 1.6, marginBottom: '20px' }}>
          Nuraxi's state-of-the-art transformer-based clinical intelligence engine —
          a 'Clinical LLM' trained on real-world patient data.
        </p>
        <div style={{
          padding: '14px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '10px',
          fontSize: '13px',
          color: 'rgba(255,255,255,0.6)',
        }}>
          Train your own clinical LLM or leverage Nuraxi's journey towards building Vitruvia
        </div>
      </div>

      {/* AI Agents Card */}
      <div style={{
        flex: '1 1 350px',
        padding: '32px',
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '20px',
        border: '1px solid rgba(255,255,255,0.1)',
      }}>
        <div style={{
          width: '50px',
          height: '4px',
          background: colors.success,
          borderRadius: '2px',
          marginBottom: '16px',
        }} />
        <h3 style={{ fontSize: '24px', fontWeight: '600', color: colors.white, marginBottom: '12px' }}>
          Clinical AI Agents
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {[
            'Review every patient encounter',
            'Identify follow-up opportunities',
            'Recommend tests & consultations',
            'Conduct research on difficult cases',
            'Monitor clinical quality',
          ].map((item, i) => (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}>
              <div style={{
                width: '22px',
                height: '22px',
                background: colors.success,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '11px',
                color: colors.white,
                flexShrink: 0,
              }}>
                ✓
              </div>
              <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.8)' }}>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

// Section 7: CTA - Try the Demo
interface Section7Props {
  onStartDemo: () => void;
}

const Section7_TryDemo = ({ onStartDemo }: Section7Props) => (
  <div style={{
    minHeight: '40vh',
    background: colors.white,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  }}>
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: colors.textLight,
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      Experience It
    </div>

    <h2 style={{
      fontSize: '40px',
      fontWeight: '300',
      color: colors.primary,
      marginBottom: '16px',
      textAlign: 'center',
    }}>
      See The <span style={{ fontWeight: '600' }}>Foundry</span> in Action
    </h2>

    <p style={{
      fontSize: '18px',
      color: colors.textLight,
      textAlign: 'center',
      maxWidth: '600px',
      marginBottom: '40px',
      lineHeight: 1.6,
    }}>
      Run our interactive demo to experience the complete data transformation pipeline —
      from fragmented clinical data to AI-ready OMOP output
    </p>

    <button
      onClick={onStartDemo}
      style={{
        padding: '18px 48px',
        fontSize: '18px',
        fontWeight: '600',
        color: colors.white,
        background: colors.primary,
        border: 'none',
        borderRadius: '50px',
        cursor: 'pointer',
        boxShadow: '0 4px 20px rgba(139, 115, 85, 0.3)',
        transition: 'transform 0.2s, box-shadow 0.2s',
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.transform = 'scale(1.05)';
        e.currentTarget.style.boxShadow = '0 6px 30px rgba(139, 115, 85, 0.4)';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.transform = 'scale(1)';
        e.currentTarget.style.boxShadow = '0 4px 20px rgba(139, 115, 85, 0.3)';
      }}
    >
      Try the Demo
    </button>

    <span style={{ fontSize: '14px', color: colors.textLight, marginTop: '16px' }}>
      Transform your data. Unlock AI. Shape the future of healthcare.
    </span>
  </div>
);

// Main Landing Component
interface FoundryLandingProps {
  onStartDemo: () => void;
}

export default function FoundryLanding({ onStartDemo }: FoundryLandingProps) {
  return (
    <div style={{ fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif" }}>
      <Section1_TheProblem />
      <Section2_WhatIsFoundry />
      <Section3_HowItWorks />
      <Section4_CorePillars />
      <Section5_Outcomes />
      <Section6_ClinicalIntelligence />
      <Section7_TryDemo onStartDemo={onStartDemo} />
    </div>
  );
}
