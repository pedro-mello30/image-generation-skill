# Whiteboard-sketch style (alternate aesthetic)

Hand-drawn dry-erase whiteboard photographed in a research office. Use this for talk decks, blog posts, social-media headers, or anywhere the look should feel like a research idea was just walked through at a whiteboard, rather than typeset for a paper.

This is **not** the default. Switch to it only when the user explicitly asks for a hand-drawn, talk, blog, or "whiteboard" look.

## Default style cues

Drop these into `text_prompts.weighted_positive`. Order matters.

```text
"Whiteboard sketch photographed in a research office, hand-drawn with dry-erase markers"            (1.5)
"Scientific charts and diagrams drawn by hand: scatter plot, Pareto frontier curve,
 bar chart, schematic boxes connected by arrows"                                                     (1.45)
"Hand-lettered axis labels, tick marks, legend, equations in chalk-marker handwriting"              (1.3)
"Color-coded markers: black for structure, blue and red for two contrasting categories,
 green for highlights, occasional orange annotation"                                                 (1.25)
"Sticky notes and dashed circles around key clusters, callout arrows with annotations"              (1.2)
"Faint smudges of half-erased prior diagrams in the background,
 subtle whiteboard texture and reflections"                                                          (1.15)
"Soft daylight from a window, slight glare on the whiteboard,
 gentle shadows from the marker strokes"                                                             (1.1)
"Editorial photographic framing, slightly off-center, three-quarter angle on the board"             (1.05)
```

And these in `text_prompts.weighted_negative`:

```text
"vector-clean LaTeX figure, pure white CAD drawing, computer-rendered UI"                           (1.4)
"clean infographic, flat 2D illustration, slide deck, dashboard"                                    (1.4)
"oversaturated rainbow colors, neon overload, cartoonish marker, comic style"                       (1.3)
"garbled text, fake equations, gibberish words, illegible scribbles"                                (1.5)
"photorealistic humans, faces, hands, body parts"                                                   (1.35)
"watermark, signature, logo, brand name"                                                            (1.4)
```

## Canonical template

```json
{
  "pipeline_configuration": {
    "job_type": "txt2img_generation",
    "meta_tags": ["whiteboard_sketch", "scientific_charts", "research_talk", "hand_drawn", "editorial"],

    "generative_parameters": {
      "surface_definition": {
        "medium": "Real dry-erase whiteboard photographed in a research office",
        "texture": "Slight reflections, faint streaks of half-erased prior diagrams, subtle whiteboard grain",
        "framing": "Three-quarter angle on the board, slightly off-center editorial composition",
        "background": "Out-of-focus office context — corner of a monitor, a few books, a coffee mug — heavily blurred"
      },

      "diagram_layout": {
        "primary_chart": {
          "type": "<scatter | line | bar | pareto_frontier | schematic_flow | matrix | radar>",
          "axes": {
            "x": "<x-axis quantity grounded in the paper>",
            "y": "<y-axis quantity grounded in the paper>",
            "tick_style": "Hand-drawn tick marks with brief numeric labels in marker handwriting"
          },
          "key_elements": [
            "<e.g. cluster of points labeled with model archetype names>",
            "<e.g. neon Pareto curve sweeping through optimal points>",
            "<e.g. dashed circle highlighting the most interesting region>"
          ],
          "annotations": [
            "<short callout text grounded in the paper's claim>",
            "<arrow pointing from a sticky note to a data point>"
          ]
        },
        "secondary_panels": [
          "<small bar chart in a corner comparing two conditions>",
          "<schematic box-and-arrow diagram of the method>",
          "<one boxed equation in marker handwriting>"
        ],
        "labels_and_legend": {
          "style": "Hand-lettered, slightly imperfect strokes, mixed cursive and print",
          "legend_position": "Compact legend in the upper-left or lower-right"
        }
      },

      "color_strategy": {
        "structural": "Black marker for axes, boxes, arrows, and most labels",
        "category_a": "Red marker for the first category",
        "category_b": "Blue marker for the second category",
        "highlights": "Green marker for the takeaway, occasional orange for annotations",
        "rule": "Never more than four marker colors; every color carries meaning"
      },

      "scene_composition": {
        "camera_settings": {
          "proximity": "Editorial wide-to-medium shot of the whiteboard",
          "depth_of_field": "Moderate — chart sharp, room blurred",
          "focus_target": "The primary chart and its main annotation",
          "lens_character": "Photographic prime lens, very low distortion"
        },
        "foreground_layers": {
          "element": "Optionally a marker resting on the tray, or a faintly visible hand mid-gesture",
          "state": "Soft blur",
          "purpose": "Hint at a live talk without dominating"
        },
        "background_layers": {
          "state": "Blurred research-office context",
          "visuals": "Warm neutral tones, gentle vignette"
        }
      },

      "lighting_and_atmosphere": {
        "style": "Natural daylight from a window with mild interior fill",
        "dynamic_range": "Balanced, slight HDR — bright board without blown highlights",
        "quality": "Soft, with subtle glare arcs across the whiteboard",
        "mood": "Curious, technical, in-the-middle-of-thinking"
      }
    },

    "text_prompts": {
      "weighted_positive": {
        "(Masterpiece, editorial photograph, ultra-detailed, 8k)": 1.5,
        "Whiteboard sketch photographed in a research office, hand-drawn with dry-erase markers": 1.5,
        "Scientific charts and diagrams drawn by hand": 1.45,
        "<paper-grounded primary diagram description>": 1.4,
        "Color-coded markers: black for structure, blue and red for contrasting categories, green for highlights": 1.25,
        "Sticky notes and dashed circles around key clusters": 1.2,
        "Faint smudges of half-erased prior diagrams": 1.15
      },
      "weighted_negative": {
        "vector-clean LaTeX figure, pure white CAD drawing, computer-rendered UI": 1.4,
        "garbled text, fake equations, gibberish words": 1.5,
        "oversaturated rainbow colors, neon overload": 1.3,
        "photorealistic humans, faces, hands": 1.35
      }
    }
  }
}
```

## When this style works well

- Talk slide hero images
- Blog post header images
- Twitter / Mastodon / LinkedIn announcement cards
- Internal "whiteboard recap" notes that look hand-drawn intentionally

## When to switch back to the paper-figure style

- The output is going into a paper or a thesis
- The user asked for "Figure N", "schematic", or "diagram"
- Typography legibility matters
- The output sits next to other paper figures and must match their aesthetic
