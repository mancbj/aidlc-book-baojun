---
name: svg-technical-diagram
description: Create or redesign editable, publication-grade SVG diagrams for technical books, academic papers, whitepapers, architecture documents, and top-tier consulting reports. Use when Codex is asked to generate, optimize, audit, or export an SVG chart, concept diagram, system architecture, process map, framework, or core formula figure with Swiss-grid precision, restrained editorial styling, reliable Chinese typography, and browser/Markdown/PNG compatibility.
---

# SVG Technical Diagram

Create diagrams that read as editorial information design, not presentation templates. Preserve the source meaning and every protected term exactly.

## Required workflow

1. Read [references/design-system.md](references/design-system.md) completely before drawing or revising an SVG.
2. Extract the visual thesis, inputs, transformation, output, feedback, and protected terminology. Freeze protected text before layout work.
3. Select the canvas. Default to `viewBox="0 0 960 540"` for books, papers, articles, and reports. Use another ratio only when the content structure requires it.
4. Draft the grid before components: 64px safe margin, 8px primary grid, 4px fine grid, aligned baselines, and intentional whitespace.
5. Establish three levels: core formula or conclusion; primary process nodes; inputs, feedback, and annotations.
6. Build the main process horizontally. When inputs are multiple, merge them through one shared rail before the transformation node. Return feedback to the shared input or constraint region.
7. Implement semantic groups and reusable CSS classes. Keep every label as editable `<text>`.
8. Run the deterministic audit:

   ```bash
   python3 scripts/audit_svg.py /absolute/path/to/figure.svg --strict
   ```

   Add `--required-text 'exact term'` once for every protected term. For AI-DLC figures, always require `𝓔 = Engineering with Exsecutio`.
9. Export to PNG with a browser-compatible renderer such as `rsvg-convert`, inspect the rendered image, and correct optical balance, collisions, clipping, and path semantics. Structural audit does not replace visual inspection.
10. Re-run the audit and repository tests after the final edit.

## Non-negotiable construction rules

- Use one card language throughout: white surface, 1px `#DDE1E7` border, `rx="4"`, and a 4–6px semantic stripe on the left.
- Never mix top stripes and left stripes. Do not use circular frames for text-bearing components.
- Use `#F7F8FA` for the background, `#252A31` for primary text, `#5F6671` for secondary text, and semantic blue, green, or purple only on small marks.
- Use `Inter, "Noto Sans SC", "PingFang SC", sans-serif`; use weights 400–500 for body text and 650–700 for titles.
- Use 1.8–2px main-flow strokes. Make feedback thinner and quieter than the main flow.
- Keep one title and one explanatory line per card. Remove decorative icons, dots, badges, large color fields, gradients, glow, glass effects, and gratuitous legends.
- Use `<defs>` for CSS variables, shared classes, markers, and any filter actually used. Do not define unused filters.
- Add a literal color declaration immediately before every CSS-variable color declaration so PNG renderers without custom-property support retain the intended palette.
- Add `vector-effect="non-scaling-stroke"` to every stroked element or enforce it in the reused class.
- Do not use `foreignObject`, embedded bitmaps, external images, scripts, animation, or text converted to paths.
- Keep the outer SVG unframed. A solid background rect may fill the viewBox but must not have a stroke.
- Never silently normalize domain terminology. `Exsecutio` is intentional and must never become `Execution`.

## Completion gate

Do not call the diagram complete until all conditions pass:

- The audit exits successfully in strict mode.
- The PNG export has no clipping and matches the SVG.
- Card edges, centers, section labels, and text baselines visibly align.
- Arrows do not cross cards or text.
- Inputs visibly converge before processing.
- Feedback visibly returns to the common input or constraint region.
- Top and bottom visual weight is balanced, and card area does not crowd the canvas.
- The protected terminology is present verbatim.

If the source meaning and the requested appearance conflict, preserve meaning and simplify the visual structure.
