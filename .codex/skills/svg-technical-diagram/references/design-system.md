# Publication-grade SVG design system

## Contents

1. Editorial direction
2. Grid and composition
3. Hierarchy and typography
4. Card system
5. Color system
6. Connectors and feedback
7. SVG engineering contract
8. Self-review rubric
9. AI-DLC protected terminology

## 1. Editorial direction

Aim for the visual quality of a technical monograph, academic figure, or top-tier consulting report. Use a Swiss grid, deliberate whitespace, exact alignment, modest typography, and semantic geometry. The figure should remain credible in grayscale.

Reject visual signals associated with ordinary slideware: oversized arrows, equal-size boxes filling every gap, centered text everywhere, heavy title bands, icon collections, decorative circles, floating badges, strong shadows, gradients, and arbitrary colors.

## 2. Grid and composition

### Canvas selection

| Context | Preferred viewBox | Rule |
|---|---:|---|
| Technical book, paper, web article, report | `0 0 960 540` | Default |
| Dense landscape architecture | `0 0 1200 675` | Preserve 16:9 |
| Taller analytical framework | `0 0 960 720` | Use only when vertical hierarchy is meaningful |
| Mobile/social card | `0 0 720 960` | Use only when explicitly requested |

### Grid

- Use a 64px safe margin on a 960×540 canvas. Never place meaningful content within 40px of an edge.
- Use an 8px primary grid and a 4px fine grid. Card frames and primary anchors land on the grid.
- Align peer cards by top edge, centerline, width, height, and text baseline.
- Keep the primary reading direction left to right.
- Keep card gaps at least 32px. Increase the gap around the transformation node instead of scaling cards to fill space.
- Keep total card area below roughly 45% of the canvas. Whitespace is structural, not unused space.
- Reserve the top 32–36% for title and thesis, the middle for the main process, and the lower 14–20% for feedback or evidence. Avoid a visually black top followed by an empty bottom.

## 3. Hierarchy and typography

Use at least three levels:

| Level | Content | Typical size | Color/weight |
|---|---|---:|---|
| Primary | Core formula or conclusion | 28–34px | `#252A31`, 650–700 |
| Secondary | Process-node titles | 20–24px | `#252A31`, 650 |
| Tertiary | Explanations, inputs, feedback | 13–16px | `#5F6671`, 400–500 |

Use this font stack:

```css
font-family: Inter, "Noto Sans SC", "PingFang SC", sans-serif;
```

Use a mono stack only for code or a formal Latin term:

```css
font-family: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
```

Keep every word as SVG `<text>`. Do not convert text to paths. Allow at least 20–24px horizontal card padding. Keep 14–18px between a card title and its explanatory line. Estimate text width before finalizing; do not rely on clipping paths to hide overflow.

## 4. Card system

Every text-bearing process component uses the same grammar:

- Fill: `#FFFFFF`
- Border: 1px `#DDE1E7`
- Radius: 4px
- Semantic accent: one 4–6px vertical stripe on the left
- Shadow: none by default; if indispensable, use one nearly invisible shared filter
- Content: one title plus one single-line explanation

Never mix top rules, bottom rules, colored outlines, and left stripes. Do not use circles or pills as text containers. A small circle is allowed only when the circle itself encodes a data point or topology node.

## 5. Color system

```text
background:  #F7F8FA
surface:     #FFFFFF
ink:         #252A31
muted:       #5F6671
border:      #DDE1E7
blue:        #0F62FE
green:       #24A148
purple:      #8A3FFC
```

- Use neutral colors for almost all area and text.
- Use blue, green, and purple only for narrow semantic stripes, a selected route, or a small signal.
- Use no more than three semantic hues in one figure.
- Do not use high-saturation fills on large rectangles.
- Do not use gradients, glow, neon, glassmorphism, or heavy dark panels.

## 6. Connectors and feedback

- Main flow: 1.8–2px, neutral `#5F6671`, one small consistent arrow marker.
- Feedback: 1.2–1.5px, lower contrast or dashed, visually subordinate to the main flow.
- Prefer orthogonal routes with modest rounded joins. Use curves only when they clarify grouping.
- Keep at least 16px between a connector and unrelated text.
- Start and end connectors at card boundaries or shared rails. Never run a connector through a card.
- Multiple inputs must converge at one visible rail or junction before entering processing.
- Feedback must return to the shared rail, shared input group, or explicit constraint area. Never return it to only one of several inputs unless that is the actual meaning.

## 7. SVG engineering contract

- Include `viewBox`, `role="img"`, `<title>`, and `<desc>`.
- Put CSS variables, shared class rules, markers, and used filters inside `<defs>`. For `librsvg` compatibility, declare a literal color before each `var(...)` color, for example `fill:#F7F8FA; fill:var(--background);`.
- Group concepts using semantic `<g id="...">`; use `data-role`, `data-card`, and `data-target` where they make relationships auditable.
- Reuse classes rather than repeating inline styles.
- Add `vector-effect="non-scaling-stroke"` to every stroked object or its shared CSS rule.
- Do not use `foreignObject`, `<image>`, external assets, embedded bitmaps, scripts, or animation.
- Keep the outermost background borderless.
- Keep markers inside the viewBox after PNG export. Leave at least 8px beyond visible arrowheads.
- Prefer simple `M`, `L`, `H`, and `V` path commands for auditable flows.
- Preserve Chinese font fallbacks and all specialist terminology verbatim.

### Recommended semantic structure

```xml
<svg viewBox="0 0 960 540" role="img" aria-labelledby="title desc">
  <title id="title">…</title>
  <desc id="desc">…</desc>
  <defs>…shared variables, classes, marker…</defs>
  <rect class="canvas" width="960" height="540"/>
  <g id="thesis" data-role="thesis">…</g>
  <g id="inputs" data-role="inputs">…card groups…</g>
  <g id="shared-input-rail" data-role="shared-input">…</g>
  <g id="transformation" data-role="process">…</g>
  <g id="output" data-role="output">…</g>
  <g id="feedback" data-role="feedback" data-target="shared-input-rail">…</g>
</svg>
```

## 8. Self-review rubric

Run `scripts/audit_svg.py` first, then inspect a PNG export at 100% and at article width.

### Structure

- Do peer components share exact x/y baselines, dimensions, and centers?
- Does every card use the same left-stripe grammar?
- Do multiple inputs merge before the process node?
- Does feedback return to the shared input or constraint region?

### Typography

- Are the title, node title, and annotation visibly distinct?
- Does every card contain only a title and one short line?
- Is any label likely to overflow after Chinese font substitution?
- Are protected terms exact and still editable text?

### Paths

- Does any arrow cross a card or unrelated label?
- Are arrowheads identical and visually restrained?
- Is feedback lighter than the main flow?

### Balance

- Is the top too dark or dense?
- Is the bottom empty without purpose?
- Is there enough quiet space around the transformation node?
- Does the diagram still work when printed in grayscale?

### Engineering

- Are `viewBox`, `<defs>`, semantic groups, CSS classes, and vector effects present?
- Are `foreignObject`, bitmap images, repeated inline styles, and clipping hacks absent?
- Does browser and PNG export preserve every edge and marker?

## 9. AI-DLC protected terminology

The following text is a domain term and must remain exact:

```text
𝓔 = Engineering with Exsecutio
```

`Exsecutio` is intentional. Never replace it with `Execution`, including in visible labels, metadata, `<desc>`, tests, or filenames.
