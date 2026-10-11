---
name: "Nestlé Accessibility Platform"
description: "A dark academic-prototype interface where accessible speech tools and research claims remain precise, inspectable, and scope-bound."
colors:
  canvas: "#0d0f14"
  surface: "#13161e"
  surface-raised: "#1a1e28"
  surface-strong: "#202532"
  border: "rgba(232,234,242,.11)"
  border-strong: "rgba(232,234,242,.2)"
  measurement-blue: "#4f8ef7"
  measurement-violet: "#7c5cfb"
  measurement-soft: "rgba(79,142,247,.12)"
  success: "#5ee2b2"
  warning: "#ffd166"
  danger: "#ff8d91"
  text: "#eef0f7"
  text-muted: "#a3a9be"
  text-subtle: "#7f879f"
typography:
  display:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "clamp(2.6rem, 6vw, 5.4rem)"
    fontWeight: 700
    lineHeight: 0.98
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "clamp(1.8rem, 3.5vw, 3.15rem)"
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.97rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.07em"
rounded:
  track: "5px"
  sm: "9px"
  md: "14px"
  brand: "11px"
  pill: "999px"
spacing:
  xs: "0.35rem"
  sm: "0.7rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
  section: "4.8rem"
components:
  inspect-button:
    backgroundColor: "transparent"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "0.45rem 0.7rem"
    height: "38px"
  inspect-button-hover:
    backgroundColor: "{colors.measurement-soft}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "0.45rem 0.7rem"
  rail-link-active:
    backgroundColor: "{colors.measurement-soft}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "0.7rem 0.75rem 0.7rem 1rem"
  verdict-supported:
    backgroundColor: "rgba(94,226,178,.09)"
    textColor: "{colors.success}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 0.7rem"
  evidence-drawer:
    backgroundColor: "#11141c"
    textColor: "{colors.text}"
    padding: "1.2rem clamp(1.2rem,4vw,2rem) 3rem"
    width: "min(480px, calc(100% - 1rem))"
---

# Design System: Nestlé Accessibility Platform

## Overview

**Creative North Star: "The Inspectable Research Canvas"**

The platform is a precise dark workspace for an academic accessibility prototype. Its near-black canvas, graphite fields, blue-to-violet measurement marks, and compact Inter typography make technical work feel focused without borrowing the visual language of a generic enterprise dashboard. Existing product surfaces may remain more task-oriented and card-based; research surfaces extend the same identity into a quieter, editorial evidence system.

The research expression is built around inspection. A reader should encounter the question and comparison before the summary metric, then be able to follow any conclusion through claim, metric, experiment, source, and limitation. Status colors are sparse and always accompanied by words, while provenance and limitations remain first-class content rather than footnotes.

**Key Characteristics:**

- Near-black canvas with graphite tonal separation rather than large decorative panels.
- Blue-violet lines and fills identify measurement, progress, selection, and provenance paths.
- Restrained semantic color communicates supported, cautionary, mismatched, and error states with explicit text.
- Large, tightly set evidence headings contrast with compact labels and tabular numeric annotations.
- Research questions form a navigable evidence spine, not a grid of interchangeable KPI cards.

## Colors

The palette is cool, dark, and measurement-led: neutrals carry structure, blue-violet carries analytical attention, and semantic hues are reserved for claims that need interpretation.

### Primary

- **Measurement Blue:** The principal analytical accent for active navigation, chart fills, progress, links, and provenance markers.

### Secondary

- **Measurement Violet:** Completes analytical gradients and marks a measured or mixed verdict without becoming a second competing brand voice.

### Tertiary

- **Supported Mint:** Used only for positively supported evidence or a confirmed current state.
- **Scope Amber:** Used for cautions, limitations, audit mismatch, and the high-visibility keyboard focus ring.
- **Error Coral:** Reserved for unavailable evidence and destructive or failed states.

### Neutral

- **Research Canvas:** The page background and deepest layer.
- **Graphite Field:** The standard panel, control, and loading surface.
- **Raised Graphite:** The interactive or nested surface used inside drawers, controls, and tracks.
- **Strong Graphite:** The densest track or comparison field.
- **Evidence White:** Primary copy and key numeric values.
- **Muted Copy:** Explanatory text that must remain comfortably readable.
- **Subtle Metadata:** Labels, captions, and secondary provenance.
- **Hairline Border / Strong Border:** Low-contrast rules create hierarchy; the stronger form is reserved for interactive boundaries and major comparison splits.

**The Measurement Color Rule.** Blue and violet mark evidence structure and interaction, never an unsupported positive conclusion.

**The Status Is Language Rule.** Semantic color is always paired with a verdict, status, or limitation label; color alone never carries meaning.

## Typography

**Display Font:** Inter (with system sans-serif fallbacks)  
**Body Font:** Inter (with system sans-serif fallbacks)  
**Label/Mono Font:** Inter for labels; SFMono-Regular or Consolas for file paths and source identifiers.

**Character:** Inter keeps the product recognizably modern and accessible while supporting dense evidence without visual noise. Tight display tracking gives research questions authority; compact labels and tabular numerals make the analytical layer exact.

### Hierarchy

- **Display** (700, fluid 2.6rem–5.4rem, 0.98): The evidence-page title only; keep it short and balanced within roughly 12 characters of measure.
- **Headline** (700, fluid 1.8rem–3.15rem, 1.08): Research questions and major conclusions, with a compact measure rather than full-width prose.
- **Title** (600–700, 0.95rem–1rem): Plot titles, evidence group headings, drawer titles, and method sections.
- **Body** (400, 0.88rem–1.18rem, 1.55): Summaries and explanatory copy, generally constrained to 68–70ch.
- **Label** (650–700, 0.67rem–0.78rem, up to 0.08em tracking): Verdict labels, rail titles, table headers, metadata, and control text; uppercase only for short categorical labels.
- **Numeric annotation** (600–650, 0.68rem–1.65rem): Tabular numerals for WER, confidence intervals, latency, and sample counts; the plot remains primary and the large number secondary.

**The Question Leads Rule.** The research question and comparison graphic establish hierarchy before any isolated metric.

**The Exact Numbers Rule.** Measured values, timestamps, and intervals use tabular numerals; source paths use the mono stack.

## Layout

The desktop research layout is a two-column evidence spine: a 224px sticky research-question rail and a fluid reading column inside a 1220px maximum container. Major sections use generous vertical separation, a single top rule, and compact internal comparison grids. The first viewport begins with scope status, a large evidence title, and the five-step claim trail before RQ1.

At 900px and below, the rail becomes a sticky horizontal strip beneath the top bar. It scrolls horizontally with a visible thin scrollbar so every research question remains reachable. Evidence comparisons collapse to two columns, and headline metrics move below their plots. At 620px and below, the claim trail becomes vertical, research sections tighten, plots use stacked tracks, action buttons span the column, and wide evidence tables remain horizontally scrollable instead of compressing their data.

Spacing follows a restrained rem rhythm: compact control gaps, 1rem evidence rows, 1.5–2rem component separation, and 4.8rem desktop section intervals. Use `clamp()` where title, section, or container spacing must scale smoothly.

**The Reading Column Rule.** Long interpretations and methodological prose stay near 68–70ch even when the evidence canvas is wider.

**The Rail Remains Reachable Rule.** Desktop and mobile navigation stay sticky; mobile overflow must expose an obvious scroll affordance.

## Elevation & Depth

The system is flat by default. Depth comes primarily from graphite tonal layering, fine borders, sticky translucent chrome, and the occasional analytical gradient. Shadows are structural: the brand mark has a compact ambient shadow, while the evidence drawer uses a large directional shadow to separate a modal layer from the inert page beneath it.

### Shadow Vocabulary

- **Brand Ambient** (`0 8px 22px rgba(0,0,0,.3)`): Keeps the small blue-violet brand mark legible against the top bar.
- **Modal Directional** (`-18px 0 55px rgba(0,0,0,.4)`): Signals that the Evidence Trail has entered from the right and now owns interaction.
- **Raised Surface** (`0 18px 55px rgba(0,0,0,.34)`): Available for genuinely elevated system surfaces, not ordinary evidence groups.

**The Flat Evidence Rule.** Research findings use rules and whitespace at rest; do not turn each metric or comparison into a floating card.

## Shapes

Corners are gently curved and utilitarian. Standard fields use a 14px radius, compact controls and evidence notices use 9px, the brand mark uses 11px, and progress tracks use 5px. Pills are reserved for brief statuses and verdicts. Circular shapes appear only as nodes, dots, or icon-only controls, preserving the evidence-spine motif.

Borders are cool translucent hairlines. Major evidence groups are usually open-sided and separated by horizontal rules; fully enclosed shapes are appropriate for interactive controls, notices, loading and error states, and the modal drawer's nested method note.

**The Open Field Rule.** Let major comparisons occupy the reading column with rules and whitespace; enclosure implies state or interaction.

## Components

### Buttons

- **Shape:** Compact, gently curved controls (9px radius) with a 38px minimum height on secondary analytical actions.
- **Primary:** Existing task surfaces may use the established blue-violet gradient and white text for the main operation.
- **Inspect:** Research evidence uses a transparent, strong-hairline button; hover shifts to a soft measurement-blue field and stronger blue border.
- **Hover / Focus:** Hover may change surface, border, or rise by 1px on task actions. Every control uses the shared 3px amber `:focus-visible` outline with 3px offset.
- **Disabled:** Reduce opacity and remove motion; keep the disabled state visibly distinct without relying on color.

### Chips

- **Style:** Fully rounded, compact, and text-led. Verdict chips combine a lightly tinted semantic field, matching text, and a low-opacity semantic border.
- **State:** Supported, mixed, caution, current, and mismatch each use explicit wording. Do not place decorative icons or unlabelled colored dots in verdict chips.

### Cards / Containers

- **Corner Style:** Standard containers use gently curved edges (14px); compact nested notes use 9px.
- **Background:** Task surfaces use graphite cards. Research findings remain transparent and are bounded by rules, while audit and error notices use low-opacity semantic fields.
- **Shadow Strategy:** Flat at rest; refer to Elevation & Depth for the few structural exceptions.
- **Border:** One-pixel translucent hairlines; increase border opacity only for controls or major evidence boundaries.
- **Internal Padding:** Typically 1–2rem, scaled with the viewport for major findings.

### Inputs / Fields

- **Style:** Raised graphite field, hairline border, inherited Inter typography, and compact 9px radius.
- **Focus:** Measurement-blue border for ordinary task inputs plus the global amber focus-visible outline for keyboard operation.
- **Error / Disabled:** Error coral identifies failure with accompanying copy; disabled controls reduce opacity and suppress transforms.

### Navigation

The sticky top bar uses a translucent canvas layer with blur and a single bottom rule. The research rail uses muted compact labels; hover adds a faint neutral field, and the active item adds a soft measurement-blue field plus a blue vertical marker and `aria-current="location"`. Below 900px, the rail becomes a horizontally scrolling sticky strip with the active state preserved.

### RQ Evidence Spine

Each research question follows a stable sequence: question, textual verdict, summary, leading comparison plot, small secondary metric annotation, accessible table, inferential or diagnostic comparisons, and key limitation. This repeated sequence allows supervisors to test like against like without reducing the page to KPI tiles.

### Evidence Trail Dialog

“Inspect evidence” opens a right-side modal that preserves the five-step chain: Claim → Metric → Experiment → Source → Limitation. The dialog traps focus, closes on Escape, returns focus to its trigger, locks page scrolling, and makes the background inert. Its visible line and nodes reuse the measurement gradient so provenance reads as a path rather than disconnected metadata.

### Loading and Error States

Loading uses restrained graphite shimmer rows with polite live-region text. Evidence-load failure uses an explicit alert, actionable repository guidance, and a high-contrast retry button. Reduced-motion preferences collapse all animations and transitions to effectively instantaneous behavior.

## Do's and Don'ts

### Do:

- **Do** preserve the near-black, graphite, Inter, and blue-violet platform identity when adding research or prototype surfaces.
- **Do** lead research findings with the question and comparison plot, keeping summary metrics as small secondary annotations.
- **Do** provide a tabular equivalent for every chart and expose source paths, selectors, statistical method, and claim limitations.
- **Do** keep active navigation programmatically current and keep modal focus contained while the background is inert.
- **Do** distinguish VAD-segmented batch inference from native streaming and label preliminary evidence as scope-bound.

### Don't:

- **Don't** replace the evidence spine with a generic grid of KPI cards or use cards to give every fact equal visual weight.
- **Don't** use green, amber, coral, blue, or violet as the only carrier of status or inferential meaning.
- **Don't** bury limitations in footnotes, tooltips, or a detached methodology page.
- **Don't** imply production readiness, validated accessibility outcomes, clinical validation, persistent speaker identity, or representative meeting-corpus coverage without evidence.
- **Don't** introduce a replacement brand language for `/research`; it is an exacting extension of the existing prototype world.
