# Nano Banana Pro `pipeline_configuration` shape

The canonical JSON structure that every render in this skill is built on. The script in [nano-banana-pro](https://github.com/) passes whatever you put in `--prompt` directly to Gemini 3 Pro Image as a single string — so the JSON below is a structured prompt, not a wire protocol. Keys exist because they steer the model, not because the API parses them.

## Top-level skeleton

```json
{
  "pipeline_configuration": {
    "job_type": "txt2img_generation",
    "meta_tags": ["..."],
    "input_reference_handling": { },
    "generative_parameters": { },
    "text_prompts": {
      "weighted_positive": { "...": 1.3 },
      "weighted_negative": { "...": 1.4 }
    }
  }
}
```

| Key | Required | Purpose |
|-----|----------|---------|
| `job_type` | yes | `txt2img_generation` or `img2img_transformation`. Drives whether `--input-image` is needed. |
| `meta_tags` | yes | 4–8 short lowercase tags. Doubles as a retrieval anchor and a soft conditioning signal. |
| `input_reference_handling` | only for `img2img_transformation` | Preservation rules for the source image (identity, structure, palette). See [img2img-preservation.md](img2img-preservation.md). |
| `generative_parameters` | yes | The "what should the image contain" block. Style-specific subkeys go here. See [paper-figure-style.md](paper-figure-style.md) and [whiteboard-style.md](whiteboard-style.md). |
| `text_prompts.weighted_positive` | yes | Positive prompts with floating-point weights, typically `1.0–1.5`. The single strongest lever you have. |
| `text_prompts.weighted_negative` | yes | Negative prompts with weights, typically `1.2–1.5`. Suppresses recurring failure modes. |

## `generative_parameters` is style-specific

The only fixed top-level key is `generative_parameters`. The subkeys inside it depend on which style you're targeting:

- **Paper figure (default)**: `figure_definition`, `layout`, `nodes`, `edges`, `typography`, `color_strategy`, `lighting_and_atmosphere`. See [paper-figure-style.md](paper-figure-style.md).
- **Whiteboard sketch (alternate)**: `surface_definition`, `diagram_layout`, `color_strategy`, `scene_composition`, `lighting_and_atmosphere`. See [whiteboard-style.md](whiteboard-style.md).
- **Img2img portrait / preservation reference**: `subject_definition`, `scene_composition`, `lighting_and_atmosphere`. See [img2img-preservation.md](img2img-preservation.md).

You can add or omit subkeys freely. The JSON only needs to parse with `json.loads`.

## Mode switch: `job_type` and `--input-image`

| Situation | `job_type` | `--input-image` | Add `input_reference_handling`? |
|-----------|------------|-----------------|---------------------------------|
| New paper figure from scratch | `txt2img_generation` | omit | no |
| Cleaning up or restyling an existing figure draft | `img2img_transformation` | required (export draft as PNG first) | yes |
| User supplies a hand sketch to formalise into a paper figure | `img2img_transformation` | required | yes |
| Paper cover / concept art from scratch | `txt2img_generation` | omit | no |
| Restyling a portrait or photograph supplied by the user | `img2img_transformation` | required | yes |

## Validation

Always parse the JSON before invoking the model. A failed `json.loads` is a free signal that beats a wasted API call.

```bash
python3 -c "import json; json.load(open('prompt.json')); print('valid')"
```

## Weight conventions

- Positive weights: `1.0` (background hint) → `1.5` (must-have). Spread weights so the most important cue is clearly heaviest.
- Negative weights: `1.2` (mild suppression) → `1.5` (hard ban). Reserve `1.5` for the failure mode you've actually seen the model produce.
- Avoid weights below `1.0` or above `1.5` — beyond that range, behaviour gets erratic.

## Why so much structure inside the prompt?

The structured fields exist to help **you** draft good `weighted_positive` lines. The model doesn't read JSON semantically, but the act of filling in `nodes` and `edges` arrays forces you to enumerate every visible element before you write the weighted prompts — which is the difference between a clean paper figure and a hallucinated mess.
