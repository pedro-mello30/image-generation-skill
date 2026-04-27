# Figure-type cheat sheet

Map the paper's claim to the right figure type before drafting the JSON. Every entry below is a value you can put in `generative_parameters.figure_definition.figure_type` and a short description of the layout that reads cleanest at paper-figure size.

## For paper-figure (default) aesthetic

| Paper claim or section | `figure_type` | Layout pattern |
|------------------------|---------------|----------------|
| Pipeline / experimental flow (e.g. dataset → model → metrics) | `schematic_flow` | 4–6 rounded rectangles in a row or L-shape, solid arrows with short labels above each arrow |
| System or method overview with grouped components | `system_overview` | Larger outer rectangle as the system boundary; inner labeled boxes; arrows for data flow |
| Architectural decomposition (e.g. dense vs MoE block) | `architectural_diagram` | Stacked or side-by-side blocks with thin internal partitions and short labels |
| Conceptual positioning vs prior work | `block_diagram` | Several inputs feeding a single "this work" box, each arrow labeled with its contribution |
| Three or four overlapping research areas with the present work in the intersection | `venn` | Three or four overlapping circles; intersection labeled with the present work |
| Two-axis design space comparison | `quadrant_map` | Cross axes with quadrant labels and a few small labeled markers; tick marks but no numerical scale |
| Distribution of items across two metrics | `scatter_plot` | Axes with tick marks, small unfilled circles for points, optional fitted line, compact legend |
| Trend across model sizes / steps / time | `line_chart` | 2–3 labeled lines with a small inset legend, axis labels in plain words |
| Category comparison on one metric | `bar_chart` | 3–6 vertical bars, hatched or grayscale fills, axis labels |
| Pairwise comparison or ablation grid | `matrix` | Square grid with row/column labels, shaded cells with numeric entries |

## For whiteboard (alternate) aesthetic

The same figure types work, but the renderings differ. In the whiteboard JSON, this value goes into `diagram_layout.primary_chart.type`. The hand-drawn medium suits some types better than others:

| Figure type | Whiteboard fit | Notes |
|-------------|----------------|-------|
| `schematic_flow` | Excellent | Box-and-arrow diagrams are what whiteboards do best |
| `pareto_frontier` | Excellent | A sweeping marker curve over a hand-drawn scatter reads strongly |
| `scatter_plot` | Good | Sparse points work; dense scatter becomes noise |
| `bar_chart` | Good | 3–4 bars max; more becomes hard to letter neatly |
| `line_chart` | OK | Limit to two or three lines; label the trend, don't expect tick precision |
| `architectural_diagram` | OK | Use color-coded internal partitions; keep overall element count low |
| `matrix` | Poor | Marker grids tend to look messy; prefer paper-figure aesthetic |
| `venn` | OK | Three overlapping circles only; four becomes confusing |
| `quadrant_map` | Excellent | Cross axes plus a handful of labeled markers reads naturally on a board |

## Combining figure types

You can combine a primary chart with one or two small secondary panels. Common compositions that work in both aesthetics:

- **Primary `schematic_flow` + inset `bar_chart`** — pipeline overview with a small ablation comparison.
- **Primary `pareto_frontier` + inset `bar_chart`** — accuracy vs efficiency with a per-prompt comparison panel.
- **Primary `system_overview` + boxed equation** — method diagram with the central formal expression.
- **Primary `block_diagram` + small `venn`** — positioning of the present work plus the overlapping research strands it draws from.

Cap any single figure at **seven distinct visual elements**. Beyond that, paper readers stop parsing.

## Picking the right type from the paper

Read the abstract and the figure list (if any) before drafting. Heuristics:

- If the paper describes a **process or pipeline**, default to `schematic_flow`.
- If it argues a **tradeoff**, default to `pareto_frontier` (whiteboard) or `quadrant_map` (paper-figure).
- If it positions itself **against prior work**, default to `block_diagram` or `venn`.
- If it compares **fixed categories on one metric**, default to `bar_chart`.
- If it shows **scaling behaviour**, default to `line_chart`.
- If it presents **ablation results**, default to `matrix` or `bar_chart`.

When in doubt, pick the simpler type. A clean `block_diagram` beats a cluttered `system_overview`.
