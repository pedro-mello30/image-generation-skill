# Provider reference

This skill supports three providers. One is selected at setup time; it can be changed at any time by re-running `python scripts/setup.py` or by editing `config.json` directly.

## Quick comparison

| Provider | Default model | Img2img | Resolutions | API key env var | Key URL |
|----------|---------------|---------|-------------|-----------------|---------|
| **Gemini** (default) | `gemini-3-pro-image-preview` | ✓ | 1K / 2K / 4K | `GEMINI_API_KEY` | https://aistudio.google.com/apikey |
| **fal.ai** | `fal-ai/imagen4/preview` | ✓ | 1K / 2K / 4K | `FAL_KEY` | https://fal.ai/dashboard/keys |
| **Replit** | delegates to Gemini or fal | ✓ | same as above | via Replit Secrets | https://replit.com — Tools → Secrets |

---

## Google AI Studio — Gemini 3 Pro Image

**Best for:** Publication-ready paper figures, whiteboard sketches, and any image where prompt adherence and text-in-image legibility matter most.

**Setup:**

```bash
export GEMINI_API_KEY=<your-key>
```

Get a key at https://aistudio.google.com/apikey (free tier available).

**Models:**

| Model ID | Notes |
|----------|-------|
| `gemini-3-pro-image-preview` | Default. High-quality, prompt-faithful. Supports 1K / 2K / 4K and img2img. |

**Resolutions:**

| Flag | Output size |
|------|-------------|
| `1K` | ~1024 px (default, use for fast iteration) |
| `2K` | ~2048 px |
| `4K` | ~4096 px (use only for final renders) |

**Img2img:** pass `--input-image path/to/ref.png`. The model auto-detects resolution from the input image unless `--resolution` is set explicitly.

**Common failures:**

| Error | Fix |
|-------|-----|
| `No API key provided.` | Set `GEMINI_API_KEY` or pass `--api-key`. |
| `quota/permission/403` | Wrong key, quota exceeded, or no access to the preview model. Try a different account. |
| `No image returned` | The model declined to generate (safety filter or policy). Simplify or rephrase the prompt. |

---

## fal.ai

**Best for:** Access to a wide model catalogue (FLUX Pro, Imagen 4, fast FLUX Schnell for iteration). Good choice when you want to compare multiple model families or when Gemini's quota is exhausted.

**Setup:**

```bash
export FAL_KEY=<your-key>
```

Get a key at https://fal.ai/dashboard/keys. Pay-per-use; no free tier but pricing is low for 1K drafts.

**Models:**

| Model ID | Best use case | Speed |
|----------|---------------|-------|
| `fal-ai/imagen4/preview` | Default. High quality, best for scientific figures. | Medium |
| `fal-ai/flux-pro` | Excellent prompt adherence, img2img support. | Medium |
| `fal-ai/flux/schnell` | Fast iteration drafts. Lower quality ceiling. | Fast |

Override the model for a single run:

```bash
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename output/draft.png \
  --model fal-ai/flux/schnell \
  --resolution 1K
```

**Resolutions:** passed as `{"width": W, "height": H}` internally. The `--resolution` flag maps:

| Flag | Width × Height |
|------|----------------|
| `1K` | 1024 × 1024 |
| `2K` | 2048 × 2048 |
| `4K` | 4096 × 4096 |

**Img2img:** pass `--input-image path/to/ref.png`. The script uploads the file to fal storage and sets `image_url` in the arguments. Requires a model that supports img2img (`fal-ai/imagen4/preview`, `fal-ai/flux-pro`, `fal-ai/flux/dev`).

**Common failures:**

| Error | Fix |
|-------|-----|
| `Error: No fal.ai API key found.` | Set `FAL_KEY` or pass `--api-key`. |
| `No image returned` / empty `images` list | Check model ID; some models return `image` instead of `images`. Open an issue. |
| Upload error for input image | Make sure the file exists and is a valid PNG/JPG. |

---

## Replit

**What it is:** Replit does not provide its own image generation API. "Replit" in this skill means *running on the Replit platform* using Replit Secrets for key management. The actual image model is either Gemini or fal.ai (you choose during setup).

**Setup:**

1. Fork or import this repo into a Replit Repl.
2. Run `python scripts/setup.py` inside the Repl and choose **Replit** as the platform.
3. When asked for the underlying provider, pick **Gemini** or **fal.ai**.
4. Go to **Tools → Secrets** in your Replit Repl and add:
   - `GEMINI_API_KEY` if you chose Gemini.
   - `FAL_KEY` if you chose fal.ai.
5. Replit Secrets are automatically loaded as environment variables — no `export` needed.

**Running:**

```bash
# inside the Repl shell
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename output/$(date +%Y-%m-%d-%H-%M-%S)-draft.png \
  --resolution 1K
```

**Notes:**

- The `scripts/providers/replit.py` adapter reads `config.json`, checks the secret, and delegates to `gemini.py` or `fal_ai.py` automatically.
- Everything else — prompt format, resolution workflow, output folder — is identical to local usage.

---

## Switching providers

At any time:

```bash
python scripts/setup.py
```

Or edit `config.json` directly:

```json
{
  "provider": "fal",
  "platform": "local",
  "model": "fal-ai/flux-pro",
  "env_var": "FAL_KEY"
}
```

For a single run without changing config, use `--provider`:

```bash
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename output/fal-test.png \
  --provider fal \
  --model fal-ai/flux/schnell \
  --resolution 1K
```

---

## config.json schema

`config.json` is written by `setup.py` and read by `generate.py`. It is gitignored — never commit it (it may reference env var names that differ between machines).

```json
{
  "provider": "gemini",
  "platform": "local",
  "model": "gemini-3-pro-image-preview",
  "env_var": "GEMINI_API_KEY"
}
```

| Key | Values | Purpose |
|-----|--------|---------|
| `provider` | `gemini`, `fal` | Which provider script to call |
| `platform` | `local`, `replit` | Informational — affects error messages in `replit.py` |
| `model` | provider-specific model ID | Injected as `--model` unless overridden on the CLI |
| `env_var` | `GEMINI_API_KEY`, `FAL_KEY` | Validated by `replit.py`; used for guidance messages |
