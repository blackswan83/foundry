# Elembic Demo - 7 Section Explanation Design Spec

## Overview

This document outlines the 7-section AIDA-framework explanation for The Elembic demo. Each section has a specific purpose in the customer journey: capturing **Attention**, building **Interest**, creating **Desire**, and driving **Action**.

---

## Brand Colors

```css
--primary: #8B7355;        /* Warm brown - main brand color */
--secondary: #6B5B4F;      /* Darker brown */
--accent: #C4A77D;         /* Gold accent */
--background: #E8E4DC;     /* Warm off-white */
--background-gradient: linear-gradient(135deg, #E8E4DC 0%, #D4CFC4 100%);
--text: #3D3D3D;
--text-light: #6B6B6B;
--success: #4A7C59;        /* Green for positive states */
--dark-bg: #2D2D2D;        /* For section 6 */
```

---

## Section 1: THE PROBLEM (Attention)

**Purpose:** Hook the audience immediately by highlighting the pain point they experience daily.

**Background:** Warm gradient (`#E8E4DC` to `#D4CFC4`)

### Layout:
```
┌────────────────────────────────────────────────────────┐
│                    THE CHALLENGE                        │  ← Small uppercase label
│                                                        │
│   Your clinical data is fragmented, siloed,           │  ← Large headline (48px)
│              and locked away                           │     "fragmented/siloed/locked" = bold
│                                                        │
│   ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                  │  ← 4 tilted cards with dashed borders
│   │ EHR │  │ Lab │  │Notes│  │Imag │                  │     Each rotated slightly (-7.5° to +7.5°)
│   │     │  │     │  │     │  │ ing │                  │     Database icon in each
│   └─────┘  └─────┘  └─────┘  └─────┘                  │
│                                                        │
│     80%              0%               ∞                │  ← Three stats (42px numbers)
│   unstructured    AI-ready      value locked          │     Labels below (14px)
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Scattered/tilted data silo cards (visual chaos)
- Dashed borders to suggest incompleteness
- Bold emphasis on pain words
- Statistics that quantify the problem

---

## Section 2: WHAT IS THE FOUNDRY (Interest)

**Purpose:** Introduce the solution with a clear, memorable visual transformation.

**Background:** White (`#FFFFFF`)

### Layout:
```
┌────────────────────────────────────────────────────────┐
│                    THE SOLUTION                         │
│                                                        │
│                   ☥ NURAXI                             │  ← Logo (28px, letter-spacing: 4px)
│                  The Elembic                           │  ← Large title (52px)
│                                                        │
│   A sovereign data transformation engine that          │  ← Subhead (22px, gray)
│   converts fragmented clinical data into an            │
│   AI-ready, research-grade intelligence platform       │
│                                                        │
│   ┌───────────┐    ┌──────────┐    ┌───────────┐      │
│   │  Raw Data │ →  │ Elembic  │ →  │OMOP Output│      │  ← Transformation visual
│   │  ░░░░░░░  │    │    ●     │    │  ████████ │      │     Before: dashed border, tilted squares
│   │  (chaos)  │    └──────────┘    │ (ordered) │      │     After: solid green border, aligned
│   └───────────┘                    └───────────┘      │
│                                                        │
│        Powered by   OMOP Common Data Model             │  ← Badge/credential bar
│                     • Global Standard                  │
└────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Clear before/after visual metaphor
- Elembic as the transformation point (brown pill button)
- OMOP credential badge
- Clean, centered layout

---

## Section 3: HOW IT WORKS (Interest)

**Purpose:** Show the 5-step process flow to build understanding and credibility.

**Background:** Warm gradient

### Layout:
```
┌────────────────────────────────────────────────────────┐
│                    THE PROCESS                          │
│                                                        │
│            How The Elembic Works                       │  ← Title (40px)
│                                                        │
│    ⬤       →      ⬤       →      ⬤       →      ⬤       →      ⬤    │
│  📥 Ingest    🔒 De-identify  🔗 Tokenize   🏷️ Encode   ✓ Output   │
│                                                        │
│  Connect to   Safe Harbor    Anonymous     ICD-10      OMOP       │
│  EHRs, Labs   removal of     linkage      SNOMED-CT   structured │
│  FHIR feeds   all PII        across       LOINC       queryable  │
│                              sources      RxNorm                  │
│                                                        │
│   ┌────────────────────────────────────────────────┐  │
│   │ 🛡️ All processing happens LOCALLY within your  │  │  ← Important note (white bg)
│   │    sovereign infrastructure                    │  │
│   └────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

**Key Elements:**
- 5 circular steps with icons (80px diameter, white bg, shadow)
- Arrows connecting steps
- Brief descriptions under each step (13px)
- Sovereignty callout box at bottom
- Final step (Output) uses green color to indicate success

---

## Section 4: FOUR PILLARS OF TRUST (Desire)

**Purpose:** Build trust through the 4 core principles that differentiate The Elembic.

**Background:** White

### Layout:
```
┌────────────────────────────────────────────────────────┐
│                   CORE PRINCIPLES                       │
│                                                        │
│              Four Pillars of Trust                     │
│                                                        │
│   ┌─────────────────────┐  ┌─────────────────────┐    │
│   │▎ 🔒 De-identified   │  │▎ 🔗 Tokenized       │    │
│   │                     │  │                     │    │
│   │ Safe Harbor         │  │ Anonymous patient   │    │
│   │ compliant removal   │  │ tokens enable       │    │
│   │ of all 18 HIPAA     │  │ longitudinal        │    │
│   │ identifiers.        │  │ tracking.           │    │
│   └─────────────────────┘  └─────────────────────┘    │
│                                                        │
│   ┌─────────────────────┐  ┌─────────────────────┐    │
│   │▎ 🏷️ Medical Coding  │  │▎ 🛡️ Sovereign       │    │
│   │                     │  │                     │    │
│   │ ICD-10, SNOMED-CT,  │  │ Data never leaves   │    │
│   │ LOINC, RxNorm       │  │ your infrastructure.│    │
│   │ standardization.    │  │ Full control.       │    │
│   └─────────────────────┘  └─────────────────────┘    │
└────────────────────────────────────────────────────────┘
```

**Key Elements:**
- 2x2 grid layout
- Each card has:
  - Colored left border (4px) matching icon color
  - Subtle gradient background
  - Icon in colored square (60px)
  - Title (24px, bold, colored)
  - Description (15px, gray)
- Color coding:
  - De-identified: Brown (#8B7355)
  - Tokenized: Blue (#4A7C9B)
  - Medical Coding: Green (#4A7C59)
  - Sovereign: Purple (#9B4A7C)

---

## Section 5: WHAT YOU CAN ACHIEVE (Desire)

**Purpose:** Show concrete outcomes/capabilities to build desire.

**Background:** Warm gradient

### Layout:
```
┌────────────────────────────────────────────────────────┐
│                    CAPABILITIES                         │
│                                                        │
│             What You Can Achieve                       │
│                                                        │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│   │   📊    │  │   🔬    │  │   🤖    │  │   🤝    │  │  ← 4 white cards
│   │Analytics│  │Research │  │AI Train │  │ Data    │  │     with shadow
│   │         │  │         │  │         │  │Sharing  │  │
│   │Longitud-│  │Deep     │  │Train AI │  │Control- │  │
│   │inal     │  │clinical │  │agents & │  │led 3rd  │  │
│   │analysis │  │research │  │models   │  │party    │  │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│                                                        │
│   ✓ HIPAA Compliant  ✓ Deployed in USA  ✓ OMOP Standard│  ← Credential bar
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Key Elements:**
- 4 equal-width cards (white bg, rounded, shadow)
- Icon in circular gradient container (70px)
- Title (18px, bold)
- Brief description (14px)
- Credential checkmarks at bottom

---

## Section 6: CLINICAL INTELLIGENCE (Desire)

**Purpose:** Showcase the AI capabilities - this is the "wow" factor section.

**Background:** Dark gradient (#2D2D2D to #1A1A1A) - contrast from other sections

### Layout:
```
┌────────────────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                     AI POWERED                         │  ← White text on dark
│                                                        │
│            Clinical Intelligence                       │  ← "Intelligence" in gold accent
│                                                        │
│   ┌───────────────────────┐  ┌───────────────────────┐│
│   │ ▔▔▔ (gold bar)        │  │ ▔▔▔ (green bar)       ││  ← Dark cards with
│   │                       │  │                       ││     semi-transparent bg
│   │     Vitruvia          │  │   Clinical AI Agents  ││
│   │                       │  │                       ││
│   │ State-of-the-art      │  │ ✓ Review encounters   ││
│   │ transformer-based     │  │ ✓ Identify follow-ups ││
│   │ clinical intelligence │  │ ✓ Recommend tests     ││
│   │ engine.               │  │ ✓ Conduct research    ││
│   │                       │  │ ✓ Monitor quality     ││
│   └───────────────────────┘  └───────────────────────┘│
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
└────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Dark theme creates visual contrast and premium feel
- Two side-by-side cards with glass-morphism effect
- Color accent bars at top of each card (gold for Vitruvia, green for Agents)
- Green checkmarks for agent capabilities
- White/light gray text hierarchy

---

## Section 7: RESEARCH ENCLAVE (Action)

**Purpose:** Drive action with partnership CTA and show the ecosystem value.

**Background:** White

### Layout:
```
┌────────────────────────────────────────────────────────┐
│                       JOIN US                          │
│                                                        │
│            Nuraxi Research Enclave                     │
│                                                        │
│   Join a global network of healthcare organizations    │
│   collaborating on frontier AI research                │
│                                                        │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│   │   💊    │  │   🏛️    │  │   🧪    │  │   🎓    │  │
│   │  Pharma │  │  Govt   │  │   AI    │  │Academia │  │
│   │         │  │         │  │Research │  │         │  │
│   │• RWE    │  │• Pop    │  │• Train  │  │• Cohort │  │
│   │• Trials │  │  health │  │  agents │  │• Models │  │
│   │• Strat. │  │• Risk   │  │• Privacy│  │• Policy │  │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│                                                        │
│              ┌──────────────────────┐                  │
│              │   Become a Partner   │                  │  ← Primary CTA button
│              └──────────────────────┘                  │     Brown bg, white text
│                                                        │     Pill shape, shadow
│   Transform your data. Unlock AI. Shape healthcare.   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Clear "Join Us" framing
- 4 stakeholder use-case cards (emoji icons)
- Prominent CTA button (pill shape, shadow)
- Aspirational tagline at bottom

---

## Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Section label | 12px | 400 | #6B6B6B |
| Main headline | 40-52px | 300 (light) | #8B7355 |
| Bold emphasis | - | 600 | same |
| Subheadline | 18-22px | 400 | #6B6B6B |
| Card title | 18-28px | 600 | varies |
| Body text | 13-15px | 400 | #6B6B6B |
| Stats | 42px | 600 | #8B7355 |

---

## Spacing

- Section padding: 60px vertical, 40px horizontal
- Card padding: 30-40px
- Gap between cards: 20-30px
- Element spacing (vertical): 12-20px

---

## Animations (Suggested)

1. **Section 1:** Cards float/wobble slightly on hover
2. **Section 3:** Steps highlight sequentially on scroll
3. **Section 4:** Cards slide in from sides
4. **Section 6:** Subtle glow on checkmarks
5. **Section 7:** CTA button pulse

---

## Mobile Considerations

- Stack cards vertically on mobile
- Reduce headline sizes by ~20%
- Process flow (Section 3) becomes vertical
- 2x2 grid becomes 1-column
- Maintain touch targets ≥44px

---

## Files Provided

1. `elembic-demo-sections.jsx` - Full React component with all 7 sections
2. This specification document

The React file can be rendered directly or used as visual reference for your development team.
