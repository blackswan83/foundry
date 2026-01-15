import React from 'react';

// Nuraxi Brand Colors
const colors = {
  primary: '#8B7355',      // Warm brown
  secondary: '#6B5B4F',    // Darker brown
  accent: '#C4A77D',       // Gold accent
  background: '#E8E4DC',   // Warm off-white
  backgroundGradient: 'linear-gradient(135deg, #E8E4DC 0%, #D4CFC4 100%)',
  text: '#3D3D3D',
  textLight: '#6B6B6B',
  white: '#FFFFFF',
  success: '#4A7C59',
  warning: '#D4A574',
  cyan: '#00A0B0',
};

// ============================================
// SECTION 1: ATTENTION - The Problem
// ============================================
const Section1_TheProblem = () => (
  <div style={{
    minHeight: '100vh',
    background: colors.backgroundGradient,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  }}>
    {/* Section Tag */}
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: colors.textLight,
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      The Challenge
    </div>
    
    {/* Main Headline */}
    <h1 style={{
      fontSize: '48px',
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
    
    {/* Visual: 4 scattered data silos */}
    <div style={{
      display: 'flex',
      gap: '30px',
      marginBottom: '50px',
      flexWrap: 'wrap',
      justifyContent: 'center',
    }}>
      {['EHR System', 'Lab Results', 'Clinical Notes', 'Imaging Reports'].map((silo, i) => (
        <div key={i} style={{
          width: '140px',
          height: '140px',
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
          {/* Database Icon */}
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={colors.primary} strokeWidth="1.5">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path d="M21 5v4c0 1.66-4 3-9 3s-9-1.34-9-3V5"/>
            <path d="M21 9v4c0 1.66-4 3-9 3s-9-1.34-9-3V9"/>
            <path d="M21 13v4c0 1.66-4 3-9 3s-9-1.34-9-3v-4"/>
          </svg>
          <span style={{ fontSize: '13px', color: colors.text, marginTop: '12px', textAlign: 'center' }}>
            {silo}
          </span>
        </div>
      ))}
    </div>
    
    {/* Problem Stats */}
    <div style={{
      display: 'flex',
      gap: '60px',
      marginTop: '20px',
    }}>
      {[
        { stat: '80%', label: 'of clinical data is unstructured' },
        { stat: '0%', label: 'AI-ready without transformation' },
        { stat: '∞', label: 'value locked inside' },
      ].map((item, i) => (
        <div key={i} style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '42px', fontWeight: '600', color: colors.primary }}>{item.stat}</div>
          <div style={{ fontSize: '14px', color: colors.textLight, maxWidth: '150px' }}>{item.label}</div>
        </div>
      ))}
    </div>
  </div>
);

// ============================================
// SECTION 2: INTEREST - What is The Foundry
// ============================================
const Section2_WhatIsFoundry = () => (
  <div style={{
    minHeight: '100vh',
    background: colors.white,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  }}>
    {/* Section Tag */}
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: colors.textLight,
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      The Solution
    </div>
    
    {/* Nuraxi Logo Placeholder */}
    <div style={{
      fontSize: '28px',
      color: colors.primary,
      marginBottom: '10px',
      fontWeight: '300',
      letterSpacing: '4px',
    }}>
      ☥ NURAXI
    </div>
    
    {/* Main Headline */}
    <h1 style={{
      fontSize: '52px',
      fontWeight: '300',
      color: colors.primary,
      textAlign: 'center',
      marginBottom: '20px',
    }}>
      The <span style={{ fontWeight: '600' }}>Foundry</span>
    </h1>
    
    <p style={{
      fontSize: '22px',
      color: colors.textLight,
      textAlign: 'center',
      maxWidth: '700px',
      marginBottom: '50px',
      lineHeight: 1.6,
    }}>
      A sovereign data transformation engine that converts fragmented clinical data 
      into an AI-ready, research-grade intelligence platform
    </p>
    
    {/* Visual: Transformation Arrow */}
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '40px',
      marginBottom: '40px',
    }}>
      {/* Before */}
      <div style={{
        width: '200px',
        height: '120px',
        background: '#F5F0EB',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        border: '2px dashed rgba(139, 115, 85, 0.3)',
      }}>
        <div style={{ fontSize: '14px', color: colors.textLight, marginBottom: '8px' }}>Raw Clinical Data</div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {[1,2,3,4].map(i => (
            <div key={i} style={{
              width: '30px', height: '35px',
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
          padding: '12px 24px',
          borderRadius: '30px',
          fontSize: '14px',
          fontWeight: '500',
          marginBottom: '8px',
        }}>
          The Foundry
        </div>
        <svg width="100" height="20" viewBox="0 0 100 20">
          <path d="M0 10 H80 L70 5 M80 10 L70 15" stroke={colors.primary} strokeWidth="2" fill="none"/>
        </svg>
      </div>
      
      {/* After */}
      <div style={{
        width: '200px',
        height: '120px',
        background: 'linear-gradient(135deg, #F0F7F4 0%, #E8F4F0 100%)',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        border: '2px solid rgba(74, 124, 89, 0.3)',
      }}>
        <div style={{ fontSize: '14px', color: colors.success, marginBottom: '8px' }}>OMOP Structured Data</div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {[1,2,3,4].map(i => (
            <div key={i} style={{
              width: '30px', height: '35px',
              background: colors.success,
              borderRadius: '4px',
              opacity: 0.6,
            }} />
          ))}
        </div>
      </div>
    </div>
    
    {/* OMOP Badge */}
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '12px 24px',
      background: '#F5F5F5',
      borderRadius: '8px',
    }}>
      <span style={{ fontSize: '14px', color: colors.textLight }}>Powered by</span>
      <span style={{ fontSize: '16px', fontWeight: '600', color: colors.text }}>OMOP Common Data Model</span>
      <span style={{ fontSize: '12px', color: colors.textLight }}>• Global Standard</span>
    </div>
  </div>
);

// ============================================
// SECTION 3: INTEREST - How It Works
// ============================================
const Section3_HowItWorks = () => (
  <div style={{
    minHeight: '100vh',
    background: colors.backgroundGradient,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  }}>
    {/* Section Tag */}
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
      fontSize: '40px',
      fontWeight: '300',
      color: colors.primary,
      marginBottom: '50px',
    }}>
      How <span style={{ fontWeight: '600' }}>The Foundry</span> Works
    </h2>
    
    {/* Process Flow Diagram */}
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '20px',
      maxWidth: '1200px',
      flexWrap: 'wrap',
      justifyContent: 'center',
    }}>
      {/* Step 1: Input */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '180px',
      }}>
        <div style={{
          width: '80px',
          height: '80px',
          background: colors.white,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          marginBottom: '16px',
        }}>
          <span style={{ fontSize: '32px' }}>📥</span>
        </div>
        <div style={{ fontSize: '16px', fontWeight: '600', color: colors.primary, marginBottom: '8px' }}>1. Ingest</div>
        <div style={{ fontSize: '13px', color: colors.textLight, textAlign: 'center', lineHeight: 1.5 }}>
          Connect to EHRs, Labs, Clinical Notes, FHIR feeds
        </div>
      </div>
      
      {/* Arrow */}
      <div style={{ paddingTop: '35px', color: colors.primary, fontSize: '24px' }}>→</div>
      
      {/* Step 2: De-identify */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '180px',
      }}>
        <div style={{
          width: '80px',
          height: '80px',
          background: colors.white,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          marginBottom: '16px',
        }}>
          <span style={{ fontSize: '32px' }}>🔒</span>
        </div>
        <div style={{ fontSize: '16px', fontWeight: '600', color: colors.primary, marginBottom: '8px' }}>2. De-identify</div>
        <div style={{ fontSize: '13px', color: colors.textLight, textAlign: 'center', lineHeight: 1.5 }}>
          Safe Harbor compliant removal of all PII
        </div>
      </div>
      
      {/* Arrow */}
      <div style={{ paddingTop: '35px', color: colors.primary, fontSize: '24px' }}>→</div>
      
      {/* Step 3: Tokenize */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '180px',
      }}>
        <div style={{
          width: '80px',
          height: '80px',
          background: colors.white,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          marginBottom: '16px',
        }}>
          <span style={{ fontSize: '32px' }}>🔗</span>
        </div>
        <div style={{ fontSize: '16px', fontWeight: '600', color: colors.primary, marginBottom: '8px' }}>3. Tokenize</div>
        <div style={{ fontSize: '13px', color: colors.textLight, textAlign: 'center', lineHeight: 1.5 }}>
          Anonymous linkage across multiple data sources
        </div>
      </div>
      
      {/* Arrow */}
      <div style={{ paddingTop: '35px', color: colors.primary, fontSize: '24px' }}>→</div>
      
      {/* Step 4: Encode */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '180px',
      }}>
        <div style={{
          width: '80px',
          height: '80px',
          background: colors.white,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          marginBottom: '16px',
        }}>
          <span style={{ fontSize: '32px' }}>🏷️</span>
        </div>
        <div style={{ fontSize: '16px', fontWeight: '600', color: colors.primary, marginBottom: '8px' }}>4. Encode</div>
        <div style={{ fontSize: '13px', color: colors.textLight, textAlign: 'center', lineHeight: 1.5 }}>
          Medical coding: ICD-10, SNOMED-CT, LOINC, RxNorm
        </div>
      </div>
      
      {/* Arrow */}
      <div style={{ paddingTop: '35px', color: colors.primary, fontSize: '24px' }}>→</div>
      
      {/* Step 5: Output */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '180px',
      }}>
        <div style={{
          width: '80px',
          height: '80px',
          background: colors.success,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          marginBottom: '16px',
        }}>
          <span style={{ fontSize: '32px' }}>✓</span>
        </div>
        <div style={{ fontSize: '16px', fontWeight: '600', color: colors.success, marginBottom: '8px' }}>5. OMOP Output</div>
        <div style={{ fontSize: '13px', color: colors.textLight, textAlign: 'center', lineHeight: 1.5 }}>
          Structured, queryable, AI-ready data
        </div>
      </div>
    </div>
    
    {/* Bottom note */}
    <div style={{
      marginTop: '50px',
      padding: '20px 40px',
      background: 'rgba(255,255,255,0.7)',
      borderRadius: '12px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
    }}>
      <span style={{ fontSize: '20px' }}>🛡️</span>
      <span style={{ fontSize: '15px', color: colors.text }}>
        All processing happens <strong>locally</strong> within your sovereign infrastructure
      </span>
    </div>
  </div>
);

// ============================================
// SECTION 4: DESIRE - Four Core Pillars
// ============================================
const Section4_CorePillars = () => (
  <div style={{
    minHeight: '100vh',
    background: colors.white,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  }}>
    {/* Section Tag */}
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
      fontSize: '40px',
      fontWeight: '300',
      color: colors.primary,
      marginBottom: '50px',
    }}>
      Four Pillars of <span style={{ fontWeight: '600' }}>Trust</span>
    </h2>
    
    {/* Four Pillars Grid */}
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(2, 1fr)',
      gap: '30px',
      maxWidth: '900px',
    }}>
      {/* Pillar 1: De-identified */}
      <div style={{
        padding: '40px',
        background: 'linear-gradient(135deg, #FDF8F3 0%, #F5EDE4 100%)',
        borderRadius: '16px',
        borderLeft: `4px solid ${colors.primary}`,
      }}>
        <div style={{
          width: '60px',
          height: '60px',
          background: colors.primary,
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px',
        }}>
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <circle cx="12" cy="8" r="4"/>
            <path d="M4 20v-2a6 6 0 0112 0v2"/>
            <line x1="4" y1="6" x2="20" y2="20"/>
          </svg>
        </div>
        <h3 style={{ fontSize: '24px', fontWeight: '600', color: colors.primary, marginBottom: '12px' }}>
          De-identified
        </h3>
        <p style={{ fontSize: '15px', color: colors.textLight, lineHeight: 1.6 }}>
          Safe Harbor compliant de-identification removes all 18 HIPAA identifiers. 
          No patient information ever leaves your control.
        </p>
      </div>
      
      {/* Pillar 2: Tokenized */}
      <div style={{
        padding: '40px',
        background: 'linear-gradient(135deg, #F3F8FD 0%, #E4EDF5 100%)',
        borderRadius: '16px',
        borderLeft: '4px solid #4A7C9B',
      }}>
        <div style={{
          width: '60px',
          height: '60px',
          background: '#4A7C9B',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px',
        }}>
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
            <line x1="10" y1="6.5" x2="14" y2="6.5"/>
            <line x1="6.5" y1="10" x2="6.5" y2="14"/>
          </svg>
        </div>
        <h3 style={{ fontSize: '24px', fontWeight: '600', color: '#4A7C9B', marginBottom: '12px' }}>
          Tokenized
        </h3>
        <p style={{ fontSize: '15px', color: colors.textLight, lineHeight: 1.6 }}>
          Anonymous patient tokens enable longitudinal tracking across multiple data 
          sources without exposing identity.
        </p>
      </div>
      
      {/* Pillar 3: Medical Coding */}
      <div style={{
        padding: '40px',
        background: 'linear-gradient(135deg, #F3FDF8 0%, #E4F5ED 100%)',
        borderRadius: '16px',
        borderLeft: `4px solid ${colors.success}`,
      }}>
        <div style={{
          width: '60px',
          height: '60px',
          background: colors.success,
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px',
        }}>
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/>
            <rect x="8" y="2" width="8" height="4" rx="1"/>
            <path d="M9 12h6"/>
            <path d="M9 16h6"/>
          </svg>
        </div>
        <h3 style={{ fontSize: '24px', fontWeight: '600', color: colors.success, marginBottom: '12px' }}>
          Medical Coding
        </h3>
        <p style={{ fontSize: '15px', color: colors.textLight, lineHeight: 1.6 }}>
          Standardized terminology using ICD-10, SNOMED-CT, LOINC, and RxNorm 
          makes data computable and interoperable.
        </p>
      </div>
      
      {/* Pillar 4: Sovereign */}
      <div style={{
        padding: '40px',
        background: 'linear-gradient(135deg, #FDF3F8 0%, #F5E4ED 100%)',
        borderRadius: '16px',
        borderLeft: '4px solid #9B4A7C',
      }}>
        <div style={{
          width: '60px',
          height: '60px',
          background: '#9B4A7C',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px',
        }}>
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="M9 12l2 2 4-4"/>
          </svg>
        </div>
        <h3 style={{ fontSize: '24px', fontWeight: '600', color: '#9B4A7C', marginBottom: '12px' }}>
          Sovereign
        </h3>
        <p style={{ fontSize: '15px', color: colors.textLight, lineHeight: 1.6 }}>
          Data never leaves your infrastructure. Full control, full compliance, 
          full sovereignty. Even Nuraxi cannot access it without permission.
        </p>
      </div>
    </div>
  </div>
);

// ============================================
// SECTION 5: DESIRE - What You Can Achieve
// ============================================
const Section5_Outcomes = () => (
  <div style={{
    minHeight: '100vh',
    background: colors.backgroundGradient,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  }}>
    {/* Section Tag */}
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
      fontSize: '40px',
      fontWeight: '300',
      color: colors.primary,
      marginBottom: '50px',
    }}>
      What You Can <span style={{ fontWeight: '600' }}>Achieve</span>
    </h2>
    
    {/* Outcomes Grid - 4 columns */}
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: '24px',
      maxWidth: '1100px',
    }}>
      {/* Outcome 1: Analytics */}
      <div style={{
        padding: '30px',
        background: colors.white,
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        textAlign: 'center',
      }}>
        <div style={{
          width: '70px',
          height: '70px',
          background: 'linear-gradient(135deg, #E8E4DC 0%, #D4CFC4 100%)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 20px',
        }}>
          <span style={{ fontSize: '32px' }}>📊</span>
        </div>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: colors.primary, marginBottom: '12px' }}>
          Analytics
        </h3>
        <p style={{ fontSize: '14px', color: colors.textLight, lineHeight: 1.5 }}>
          Longitudinal analysis across conditions, departments, outcomes, and patient journeys
        </p>
      </div>
      
      {/* Outcome 2: Research */}
      <div style={{
        padding: '30px',
        background: colors.white,
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        textAlign: 'center',
      }}>
        <div style={{
          width: '70px',
          height: '70px',
          background: 'linear-gradient(135deg, #E8E4DC 0%, #D4CFC4 100%)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 20px',
        }}>
          <span style={{ fontSize: '32px' }}>🔬</span>
        </div>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: colors.primary, marginBottom: '12px' }}>
          Research
        </h3>
        <p style={{ fontSize: '14px', color: colors.textLight, lineHeight: 1.5 }}>
          Deep clinical research from connected, structured datasets
        </p>
      </div>
      
      {/* Outcome 3: AI Training */}
      <div style={{
        padding: '30px',
        background: colors.white,
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        textAlign: 'center',
      }}>
        <div style={{
          width: '70px',
          height: '70px',
          background: 'linear-gradient(135deg, #E8E4DC 0%, #D4CFC4 100%)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 20px',
        }}>
          <span style={{ fontSize: '32px' }}>🤖</span>
        </div>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: colors.primary, marginBottom: '12px' }}>
          AI Training
        </h3>
        <p style={{ fontSize: '14px', color: colors.textLight, lineHeight: 1.5 }}>
          Train AI agents and models on your de-identified clinical data
        </p>
      </div>
      
      {/* Outcome 4: Data Sharing */}
      <div style={{
        padding: '30px',
        background: colors.white,
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        textAlign: 'center',
      }}>
        <div style={{
          width: '70px',
          height: '70px',
          background: 'linear-gradient(135deg, #E8E4DC 0%, #D4CFC4 100%)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 20px',
        }}>
          <span style={{ fontSize: '32px' }}>🤝</span>
        </div>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: colors.primary, marginBottom: '12px' }}>
          Data Sharing
        </h3>
        <p style={{ fontSize: '14px', color: colors.textLight, lineHeight: 1.5 }}>
          Controlled third-party access to de-identified OMOP data
        </p>
      </div>
    </div>
    
    {/* Credential Bar */}
    <div style={{
      marginTop: '50px',
      display: 'flex',
      gap: '40px',
      alignItems: 'center',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '18px' }}>✓</span>
        <span style={{ fontSize: '14px', color: colors.text }}>HIPAA Compliant</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '18px' }}>✓</span>
        <span style={{ fontSize: '14px', color: colors.text }}>Deployed in USA HIEs</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '18px' }}>✓</span>
        <span style={{ fontSize: '14px', color: colors.text }}>OMOP Standard</span>
      </div>
    </div>
  </div>
);

// ============================================
// SECTION 6: DESIRE - Clinical Intelligence
// ============================================
const Section6_ClinicalIntelligence = () => (
  <div style={{
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #2D2D2D 0%, #1A1A1A 100%)',
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  }}>
    {/* Section Tag */}
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
      fontSize: '40px',
      fontWeight: '300',
      color: colors.white,
      marginBottom: '20px',
    }}>
      Clinical <span style={{ fontWeight: '600', color: colors.accent }}>Intelligence</span>
    </h2>
    
    <p style={{
      fontSize: '18px',
      color: 'rgba(255,255,255,0.7)',
      textAlign: 'center',
      maxWidth: '600px',
      marginBottom: '50px',
    }}>
      The Foundry unlocks AI and agentic power for immediate clinical and commercial impact
    </p>
    
    {/* Two Cards Side by Side */}
    <div style={{
      display: 'flex',
      gap: '40px',
      maxWidth: '900px',
    }}>
      {/* Vitruvia Card */}
      <div style={{
        flex: 1,
        padding: '40px',
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '20px',
        border: '1px solid rgba(255,255,255,0.1)',
      }}>
        <div style={{
          width: '50px',
          height: '4px',
          background: colors.accent,
          borderRadius: '2px',
          marginBottom: '20px',
        }} />
        <h3 style={{ fontSize: '28px', fontWeight: '600', color: colors.white, marginBottom: '16px' }}>
          Vitruvia
        </h3>
        <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.7)', lineHeight: 1.7, marginBottom: '24px' }}>
          Nuraxi's state-of-the-art transformer-based clinical intelligence engine — 
          a 'Clinical LLM' trained on real-world patient data.
        </p>
        <div style={{
          padding: '16px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '12px',
          fontSize: '14px',
          color: 'rgba(255,255,255,0.6)',
        }}>
          Train your own clinical LLM or leverage Nuraxi's journey towards building Vitruvia
        </div>
      </div>
      
      {/* AI Agents Card */}
      <div style={{
        flex: 1,
        padding: '40px',
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '20px',
        border: '1px solid rgba(255,255,255,0.1)',
      }}>
        <div style={{
          width: '50px',
          height: '4px',
          background: colors.success,
          borderRadius: '2px',
          marginBottom: '20px',
        }} />
        <h3 style={{ fontSize: '28px', fontWeight: '600', color: colors.white, marginBottom: '16px' }}>
          Clinical AI Agents
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
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
              gap: '12px',
            }}>
              <div style={{
                width: '24px',
                height: '24px',
                background: colors.success,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                color: colors.white,
              }}>
                ✓
              </div>
              <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.8)' }}>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

// ============================================
// SECTION 7: ACTION - Research Enclave CTA
// ============================================
const Section7_ResearchEnclave = () => (
  <div style={{
    minHeight: '100vh',
    background: colors.white,
    padding: '60px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  }}>
    {/* Section Tag */}
    <div style={{
      fontSize: '12px',
      letterSpacing: '3px',
      color: colors.textLight,
      marginBottom: '20px',
      textTransform: 'uppercase',
    }}>
      Join Us
    </div>
    
    <h2 style={{
      fontSize: '44px',
      fontWeight: '300',
      color: colors.primary,
      marginBottom: '20px',
      textAlign: 'center',
    }}>
      Nuraxi <span style={{ fontWeight: '600' }}>Research Enclave</span>
    </h2>
    
    <p style={{
      fontSize: '20px',
      color: colors.textLight,
      textAlign: 'center',
      maxWidth: '700px',
      marginBottom: '50px',
      lineHeight: 1.6,
    }}>
      Join a global network of healthcare organizations collaborating on frontier AI 
      research that advances clinical intelligence — and shares commercial benefits
    </p>
    
    {/* Use Case Grid */}
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: '20px',
      maxWidth: '1000px',
      marginBottom: '50px',
    }}>
      {[
        { icon: '💊', title: 'Pharma', items: ['Real world evidence', 'Patient stratification', 'Clinical trial design'] },
        { icon: '🏛️', title: 'Government', items: ['Population health', 'Risk stratification', 'Prevention modeling'] },
        { icon: '🧪', title: 'AI Researchers', items: ['Train clinical agents', 'Privacy-preserving ML', 'Model evaluation'] },
        { icon: '🎓', title: 'Academia', items: ['Cohort discovery', 'Predictive models', 'Outcome research'] },
      ].map((item, i) => (
        <div key={i} style={{
          padding: '24px',
          background: colors.backgroundGradient,
          borderRadius: '12px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>{item.icon}</div>
          <h4 style={{ fontSize: '16px', fontWeight: '600', color: colors.primary, marginBottom: '12px' }}>
            {item.title}
          </h4>
          {item.items.map((subitem, j) => (
            <div key={j} style={{ fontSize: '13px', color: colors.textLight, marginBottom: '4px' }}>
              {subitem}
            </div>
          ))}
        </div>
      ))}
    </div>
    
    {/* CTA Button */}
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '16px',
    }}>
      <button style={{
        padding: '18px 48px',
        fontSize: '18px',
        fontWeight: '600',
        color: colors.white,
        background: colors.primary,
        border: 'none',
        borderRadius: '50px',
        cursor: 'pointer',
        boxShadow: '0 4px 20px rgba(139, 115, 85, 0.3)',
      }}>
        Become a Partner
      </button>
      <span style={{ fontSize: '14px', color: colors.textLight }}>
        Transform your data. Unlock AI. Shape the future of healthcare.
      </span>
    </div>
  </div>
);

// ============================================
// FULL DEMO COMPONENT
// ============================================
export default function FoundryDemoSections() {
  return (
    <div style={{ fontFamily: "'Inter', -apple-system, sans-serif" }}>
      <Section1_TheProblem />
      <Section2_WhatIsFoundry />
      <Section3_HowItWorks />
      <Section4_CorePillars />
      <Section5_Outcomes />
      <Section6_ClinicalIntelligence />
      <Section7_ResearchEnclave />
    </div>
  );
}
