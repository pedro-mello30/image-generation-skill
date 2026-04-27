# Img2img preservation rules

Use this reference when `job_type` is `img2img_transformation` — i.e., the user supplies an existing image that should be restyled, extended, or formalised rather than generated from scratch.

The block below is the original Nano Banana 3.0 user-supplied template (verbatim). It defines the canonical shape for `input_reference_handling.preservation_rules`. The structure is what matters; the specific portrait content is just the example.

## When to use img2img

| Situation | `job_type` | `--input-image` |
|-----------|------------|-----------------|
| Cleaning up or restyling an existing figure draft | `img2img_transformation` | required (export draft as PNG first) |
| User supplies a hand sketch to formalise into a paper figure | `img2img_transformation` | required |
| Restyling a portrait or photograph supplied by the user | `img2img_transformation` | required |
| New figure or concept image from scratch | `txt2img_generation` | omit |

## Shape of `input_reference_handling`

```json
"input_reference_handling": {
  "preservation_rules": {
    "<aspect_to_preserve>": {
      "strength": 1.0,
      "instruction": "<plain-English instruction>",
      "technique": "<technique hint, e.g. FaceID / IP-Adapter Strong>"
    }
  }
}
```

Each rule names one aspect of the source image that must be preserved. Common aspects:

- `structure` — overall layout, node positions, axis arrangement
- `color_palette` — keep the source's colors; useful when restyling figures that already have a brand palette
- `facial_identity` — for portrait inputs
- `composition` — framing, focal length, vantage point
- `typography` — preserve text content even while restyling fonts

`strength` is `0.0–1.0`. Use `1.0` for hard preservation; lower values let the model deviate.

## When to use it for paper figures

The most common paper-figure use case is **formalising a hand sketch into a clean paper figure**. The user uploads a photo of a whiteboard or a notebook sketch; you want to keep the exact layout (node positions, edge routing) but restyle to LaTeX-clean strokes and Computer Modern Serif typography.

Sketch-to-paper-figure preservation rules:

```json
"input_reference_handling": {
  "preservation_rules": {
    "structure": {
      "strength": 1.0,
      "instruction": "Preserve the exact node layout, count, and connections from the source sketch. Keep the same spatial arrangement.",
      "technique": "ControlNet Strong"
    },
    "node_labels": {
      "strength": 1.0,
      "instruction": "Preserve every visible label from the source sketch verbatim; do not invent new labels or rename existing ones.",
      "technique": "OCR-guided"
    },
    "color_palette": {
      "strength": 0.0,
      "mode": "override_to_blackwhite",
      "instruction": "Discard source colors. Render strictly black ink on white."
    }
  }
}
```

Combine that block with the [paper-figure-style.md](paper-figure-style.md) `weighted_positive` cues, and pass `--input-image path/to/sketch.png` on the command line.

## Original portrait shape (verbatim)

Kept here only as a shape reference. **Do not** use this as the default for paper visualizations — it's a portrait restyling template.

```
Gemini Nano Banana 3.0

Prompt:

{
  "pipeline_configuration": {
    "job_type": "img2img_transformation",
    "meta_tags": ["macro", "beauty", "soft_focus", "realism"],
    
    "input_reference_handling": {
      "preservation_rules": {
        "facial_identity": {
          "strength": 1.0,
          "instruction": "Strict 100% preservation of facial geometry and features.",
          "technique": "FaceID / IP-Adapter Strong"
        },
        "color_palette": {
          "target": "Hair Color",
          "mode": "inherit_from_source",
          "instruction": "Do not hallucinate new hair color. Map source color to new hair texture."
        }
      }
    },

    "generative_parameters": {
      "subject_definition": {
        "hair_morphology": {
          "length": "Short",
          "texture_type": "Wavy",
          "styling_aesthetic": "Intentionally messy, artfully disheveled",
          "micro_details": "Fine strands falling across forehead and near eyes",
          "color_override": null
        },
        "facial_details": {
          "expression": "Serene, gentle",
          "makeup_style": "Natural, soft-beauty approach",
          "surface_texture": "Ultra-clean skin with visible macro pores"
        }
      },

      "scene_composition": {
        "camera_settings": {
          "proximity": "Extreme Close-Up (Macro)",
          "depth_of_field": "Ultra-shallow",
          "focus_target": "Eyes",
          "lens_character": "Soft beauty lens"
        },
        "foreground_layers": {
          "element": "Hand",
          "state": "Partially blurred",
          "purpose": "Framing effect, adding depth and intimacy"
        },
        "background_layers": {
          "state": "Fully out of focus",
          "visuals": "Pastel, soft tones",
          "bokeh_quality": "Strong, smooth, creamy"
        }
      },

      "lighting_and_atmosphere": {
        "style": "Soft-beauty photography",
        "dynamic_range": "High (HDR)",
        "quality": "Airy, bright, diffused",
        "reflections": {
          "eyes": "Crisp, sharp catchlights",
          "lips": "Soft, natural shine"
        }
      }
    },

    "text_prompts": {
      "weighted_positive": {
        "(Masterpiece, Best Quality, 8k, Macro Photo)": 1.5,
        "Extreme close-up of young woman with serene gentle expression": 1.3,
        "Short wavy messy hair with stray wisps over eyes": 1.2,
        "Hand in foreground partially blurred framing the face": 1.2,
        "Macro skin texture, pores visible, individual hair strands": 1.4,
        "Ultra-sharp eyes with crisp reflections": 1.3,
        "Soft pastel bokeh background": 1.1,
        "Soft diffused lighting, airy aesthetic": 1.0
      },
      "weighted_negative": {
        "alteration of face, new hair color, long hair": 1.5,
        "plastic skin, airbrushed, smooth": 1.4,
        "cartoon, 3d render, illustration": 1.3,
        "deep focus, sharp background, clutter": 1.2,
        "deformed hand, bad anatomy": 1.4
      }
    }
  }
}
```
