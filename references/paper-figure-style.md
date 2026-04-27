# Paper-figure style (default aesthetic)

Clean black-on-white schematic suitable for embedding directly into a LaTeX paper. Rounded rectangle nodes, thin strokes, labeled arrows, Computer Modern Serif typography. The target is a figure that could sit next to other figures in a real paper and not look out of place.

## Default style cues

Drop these into `text_prompts.weighted_positive` (verbatim or paraphrased). Order matters — strongest cue first.

```text
"Publication-ready scientific figure for a research paper, LaTeX style, vector-clean look"          (1.5)
"Pure white background, no decoration, no shading, no gradients, no drop shadows"                   (1.45)
"Rounded-rectangle nodes with thin black 1pt stroke and short text labels inside,
 generous internal padding"                                                                          (1.4)
"Solid black arrows with simple triangular arrowheads connecting the nodes,
 optional short text labels above each arrow"                                                        (1.4)
"Computer Modern Serif typography, the typography of LaTeX papers, crisp and legible"               (1.35)
"Strictly black ink on white, optional single accent gray for secondary lines, no other colors"     (1.3)
"Axis-aligned layout, generous whitespace, balanced spacing between nodes"                          (1.25)
"A figure caption in italic Computer Modern beneath the diagram,
 e.g. 'Figure 1: <short caption>'"                                                                  (1.2)
```

And these in `text_prompts.weighted_negative` to suppress the failure modes this aesthetic is most prone to:

```text
"garbled text, gibberish words, misspelled labels, fake equations, illegible runes"                 (1.5)
"3D rendering, isometric perspective, drop shadows, gradients, glossy surfaces"                     (1.45)
"colorful infographic, marketing slide, dashboard UI, brand iconography, emojis"                    (1.4)
"hand-drawn, sketchy lines, marker strokes, whiteboard, paper texture, watercolor"                  (1.4)
"photorealistic humans, faces, hands, body parts, mannequins, mascots"                              (1.4)
"watermark, signature, logo, brand name, school crest, page numbers, headers"                       (1.4)
"cluttered layout, overlapping arrows, crossed lines, more than seven nodes"                        (1.3)
"blurry, noisy, jpeg artifacts, low contrast, rasterised line art"                                  (1.3)
```

## Canonical template

```json
{
  "pipeline_configuration": {
    "job_type": "txt2img_generation",
    "meta_tags": ["paper_figure", "latex_style", "schematic", "vector_clean", "black_and_white", "scientific"],

    "generative_parameters": {
      "figure_definition": {
        "figure_type": "<schematic_flow | block_diagram | system_overview | quadrant_map | venn | scatter_plot | line_chart | bar_chart | architectural_diagram | matrix>",
        "caption": "Figure 1: <short, paper-grounded caption text>",
        "aspect_ratio": "<16:9 | 4:3 | 3:2 | square>",
        "background": "Pure white, no fill, no border"
      },

      "layout": {
        "structure": "<e.g. five rounded rectangle nodes arranged in an L-shape, four feeding into one>",
        "alignment": "Axis-aligned, generous whitespace, balanced",
        "node_padding": "Generous internal padding, text never touches node borders",
        "edge_routing": "Straight or right-angled lines only, no diagonal crossings"
      },

      "nodes": [
        { "id": "n1", "shape": "rounded_rectangle", "label": "<1-4 words>" },
        { "id": "n2", "shape": "rounded_rectangle", "label": "<1-4 words>" }
      ],

      "edges": [
        { "from": "n1", "to": "n2", "label": "<optional 1-3 words>", "style": "solid" }
      ],

      "typography": {
        "family": "Computer Modern Serif (LaTeX default)",
        "weight": "Regular for labels, italic for the caption",
        "size_hierarchy": "Caption smallest, node labels medium, section labels largest if any"
      },

      "color_strategy": {
        "primary": "Black ink",
        "secondary": "At most one neutral gray for de-emphasised lines",
        "rule": "No additional colors. If the user asks for a single accent, use a single muted hue at low saturation"
      },

      "lighting_and_atmosphere": {
        "style": "Flat document rendering, no lighting, no shadows",
        "post_processing": "None — vector-clean output"
      }
    },

    "text_prompts": {
      "weighted_positive": {
        "Publication-ready scientific figure for a research paper, LaTeX style, vector-clean look": 1.5,
        "Pure white background, no decoration, no shading, no gradients": 1.45,
        "Rounded-rectangle nodes with thin black 1pt stroke and short text labels inside, generous internal padding": 1.4,
        "Solid black arrows with simple triangular arrowheads connecting the nodes, optional short text labels above each arrow": 1.4,
        "Computer Modern Serif typography, the typography of LaTeX papers, crisp and legible": 1.35,
        "<paper-grounded primary layout description from the résumé visual hooks>": 1.45,
        "<paper-grounded node labels and edge labels listed explicitly>": 1.4,
        "Strictly black ink on white, no color": 1.3,
        "Axis-aligned layout, generous whitespace": 1.25,
        "Italic Computer Modern caption beneath the figure: 'Figure 1: <short caption>'": 1.2
      },
      "weighted_negative": {
        "garbled text, gibberish words, misspelled labels, fake equations": 1.5,
        "3D rendering, isometric perspective, drop shadows, gradients": 1.45,
        "colorful infographic, marketing slide, dashboard UI, emojis": 1.4,
        "hand-drawn, sketchy lines, marker strokes, whiteboard, paper texture": 1.4,
        "photorealistic humans, faces, hands, body parts": 1.4,
        "watermark, signature, logo, brand name, page numbers": 1.4,
        "cluttered layout, overlapping arrows, crossed lines": 1.3,
        "blurry, noisy, jpeg artifacts, low contrast": 1.3
      }
    }
  }
}
```

## Text-rendering hard rules

Diffusion models still mangle long labels, made-up acronyms, and equations. To stay paper-ready:

- Every node label is **1–4 real English words**. No invented acronyms inside nodes.
- List node and edge labels **verbatim** in `weighted_positive` — the model is more likely to honor exactly-quoted strings.
- At most **one boxed equation per figure**, written in standard LaTeX form. More than that almost always becomes gibberish.
- If a label still renders garbled after two retries, simplify it (drop a word, swap in a synonym, or move it into the caption).
- For absolute typographic fidelity, prefer generating **TikZ / PGF / matplotlib / mermaid code** instead. This skill is best for figures whose layout is hard to express in code (organic compositions, spatial metaphors, mixed-style overviews).

## Authoring tips

- The strongest single lever for paper-quality output is the **negative** prompt against `hand-drawn, sketchy, marker, whiteboard, gradients, drop shadows`. Keep those weights at 1.4–1.5.
- Always include `paper_figure`, `latex_style`, and `vector_clean` in `meta_tags`.
- Keep figures small in element count. **Five rounded rectangles read as a paper figure; fifteen read as a slide.**
- If the figure has axes, name the quantities on each axis in plain words; avoid LaTeX macros (`\mathcal{}`, `\frac{}{}`) — the model can't render them.
- Don't expect the model to invent labels you didn't write. List every visible word explicitly.
