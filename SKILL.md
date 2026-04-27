---
name: paper-to-image
description: Turn a research paper (PDF, arXiv URL, .docx, HTML, .tex export) into a publication-ready figure via a 4-step pipeline — read the paper, write an in-depth résumé, build a Nano Banana Pro pipeline_configuration JSON prompt, then render with the configured image provider (Gemini, fal.ai, or Replit). Default output is a clean LaTeX-style schematic figure suitable for embedding in a paper. Use when the user asks for a paper figure, diagram, schematic, system overview, related-work positioning figure, cover, or concept image from a paper, abstract, or scientific PDF.
---

# Paper → Summary → JSON Prompt → Image

Four sequential steps. Do not skip any. Each step's output feeds the next.

```
Paper -> Markdown text -> In-depth résumé -> Nano Banana JSON -> PNG
```

## First-run setup

Check if the provider is configured:

```bash
test -f config.json && python -c "import json; c=json.load(open('config.json')); print('Provider:', c['provider'], '|', 'Model:', c.get('model','n/a'))" || echo "Not configured"
```

If not configured — or if the user wants to change provider — run the interactive setup:

```bash
python scripts/setup.py
```

This asks:
1. Which provider: **Gemini** (default), **fal.ai**, or **Replit** platform.
2. Which model within that provider.
3. Checks whether the required API key env var is set, and prints where to get one if not.

Writes `config.json` (gitignored). All subsequent renders read from it automatically. Re-run at any time to switch providers.

See [`references/providers.md`](references/providers.md) for API key setup, model lists, and per-provider caveats.

✋ **Stop here if** the provider is not yet configured and the user hasn't set their API key. Ask which provider they prefer before continuing.

## Workflow checklist

Copy this checklist into the chat and tick items as you progress:

```
- [ ] Setup: provider configured (python scripts/setup.py)
- [ ] Step 1: Read the paper (convert to Markdown)
- [ ] Step 2: Write in-depth résumé
- [ ] Step 3: Build pipeline_configuration JSON
- [ ] Step 4: Generate the image (1K draft, then 4K final)
```

## Step 1 — Read the paper

Convert any source to Markdown so the full text is available. Use the [`markdown-converter`](https://github.com/) skill (or `uvx markitdown` directly).

```bash
uvx markitdown path/to/paper.pdf -o paper.md
```

Notes:

- Works for PDF, .docx, .pptx, HTML, EPub, and more.
- For arXiv links, prefer the PDF URL; for HTML-only sources, save the page first or paste the full text.
- For scanned PDFs, re-run with Azure Document Intelligence (`-d -e ENDPOINT`).
- Read the resulting `paper.md` before continuing.

✋ **Stop here if** the paper text is too short (< 500 words) or you cannot extract clean text. Tell the user, ask for a different source.

## Step 2 — In-depth résumé

Write the résumé directly in chat (or save to `summary.md` if the user asks). It must be deep, not an abstract. Use this outline:

```markdown
# <Paper title> — In-depth résumé

## Problem & motivation
What gap or question the paper addresses and why it matters.

## Method
Core technique, architecture, formalism, or experimental design. Include
notable equations, diagrams, or pseudocode the paper relies on.

## Key results
Quantitative findings, tables, headline numbers, ablations.

## Limitations & open questions
Failure modes, caveats, and what the authors flag as future work.

## Visual hooks
3–5 concrete image-able concepts: metaphors, central figures, mechanisms,
or aesthetics that could anchor a single strong illustration. This list
seeds Step 3.
```

✋ **Stop here if** you cannot find at least one concrete visual hook. A weak hook produces a generic image; better to ask the user which aspect of the paper they want illustrated.

## Step 3 — Build the pipeline_configuration JSON

Pick one visual hook from Step 2 and translate it into a single valid JSON object using the Nano Banana Pro shape.

**Default aesthetic: publication-ready paper figure.** Clean black-on-white schematic, rounded rectangle nodes, thin strokes, labeled arrows, Computer Modern Serif typography (LaTeX style). The result should look like Figure 1 of a real paper, not concept art. Switch to the **whiteboard-sketch** alternate only when the user explicitly asks for a hand-drawn / talk / blog aesthetic.

Read these references before drafting:

- [`references/nano-banana-prompt-shape.md`](references/nano-banana-prompt-shape.md) — the canonical JSON skeleton, weight conventions, mode-switch table.
- [`references/paper-figure-style.md`](references/paper-figure-style.md) — default LaTeX-style cues, full template, text-rendering hard rules.
- [`references/figure-types.md`](references/figure-types.md) — cheat sheet mapping paper claims to `figure_type` values.
- [`references/whiteboard-style.md`](references/whiteboard-style.md) — alternate hand-drawn template (use only on request).
- [`references/img2img-preservation.md`](references/img2img-preservation.md) — preservation rules when restyling an existing image.

**Text-rendering reality check.** Diffusion models — including Gemini 3 Pro Image — frequently mangle long labels, made-up acronyms, and equations. To stay paper-ready:

- Keep every label 1–4 real English words. No invented terms inside boxes.
- At most one boxed equation per figure, in plain LaTeX-rendered Computer Modern.
- Be ready to re-render 2–4 times; tweak the offending label as a separate `weighted_positive` line.
- For absolute typographic fidelity, prefer generating TikZ / PGF / matplotlib / mermaid code instead. This skill is best for figures whose layout is hard to express in code (organic compositions, spatial metaphors, mixed-style overviews).

Required top-level shape:

```json
{
  "pipeline_configuration": {
    "job_type": "txt2img_generation",
    "meta_tags": ["..."],
    "generative_parameters": { },
    "text_prompts": {
      "weighted_positive": { "...": 1.3 },
      "weighted_negative": { "...": 1.4 }
    }
  }
}
```

Save the JSON to a file (avoids shell-escaping pain) and validate before invoking the model:

```bash
cat > prompt.json <<'JSON'
{ "pipeline_configuration": { ... } }
JSON
python3 -c "import json; json.load(open('prompt.json')); print('valid')"
```

✋ **Stop here unless** `json.load` returns `valid`. A failed parse is a free signal that beats a wasted API call.

## Step 4 — Generate the image

Default workflow: **1K draft → iterate → 4K final.** All renders go into `output/`. The dispatcher (`scripts/generate.py`) reads `config.json` for provider and model, then calls the right backend.

Filename convention: `output/yyyy-mm-dd-hh-mm-ss-<slug>.png`.

Draft (txt2img):

```bash
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename "output/$(date +%Y-%m-%d-%H-%M-%S)-paper-draft.png" \
  --resolution 1K
```

✋ **Stop here unless** the 1K draft is on-target. Iterate on `prompt.json` first; one prompt change per iteration so cause and effect stay visible. Only escalate to 4K once the draft is right — 4K runs are slower and more expensive.

Final (4K) once the prompt looks right:

```bash
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename "output/$(date +%Y-%m-%d-%H-%M-%S)-paper-final.png" \
  --resolution 4K
```

Img2img (only when a reference image is provided):

```bash
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename "output/$(date +%Y-%m-%d-%H-%M-%S)-paper-edit.png" \
  --input-image path/to/reference.png \
  --resolution 2K
```

Override provider or model for a single run without changing config:

```bash
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename "output/$(date +%Y-%m-%d-%H-%M-%S)-fal-draft.png" \
  --provider fal \
  --model fal-ai/flux/schnell \
  --resolution 1K
```

Always run from the project root so `output/` resolves correctly.

## API keys

Keys are read from environment variables — never stored in any committed file. Each provider uses a different variable:

| Provider | Env var | Get key at |
|----------|---------|------------|
| Gemini | `GEMINI_API_KEY` | https://aistudio.google.com/apikey |
| fal.ai | `FAL_KEY` | https://fal.ai/dashboard/keys |
| Replit | set via Replit Secrets (same vars above) | Tools → Secrets in your Repl |

Add to your shell profile (e.g. `~/.bashrc` or `~/.zshrc`):

```bash
export GEMINI_API_KEY=<your-key>   # for Gemini
export FAL_KEY=<your-key>          # for fal.ai
```

If the user pasted a key in chat, treat it as compromised — ask them to rotate it before continuing.

See [`references/providers.md`](references/providers.md) for full setup, model options, and common error fixes.

## Iteration tips

- Keep the JSON file; tweak fields between runs rather than rewriting from scratch.
- One change per iteration so cause and effect are clear.
- If the result drifts from the paper, strengthen the matching `weighted_positive` line by `+0.1` or add a precise `weighted_negative`.
- Re-render with the same filename slug plus `-v2`, `-v3` rather than overwriting — keeps the iteration history visible.
- If a label still renders garbled after two retries, simplify it (drop a word, swap in a synonym, or move it into the caption instead).

## Resources

- [`references/providers.md`](references/providers.md) — provider setup, API keys, model lists, common failures.
- [`references/nano-banana-prompt-shape.md`](references/nano-banana-prompt-shape.md) — JSON skeleton and conventions.
- [`references/paper-figure-style.md`](references/paper-figure-style.md) — default LaTeX paper-figure aesthetic.
- [`references/whiteboard-style.md`](references/whiteboard-style.md) — alternate whiteboard-sketch aesthetic.
- [`references/figure-types.md`](references/figure-types.md) — figure-type cheat sheet.
- [`references/img2img-preservation.md`](references/img2img-preservation.md) — img2img preservation rules.
- [`scripts/setup.py`](scripts/setup.py) — interactive provider setup.
- [`scripts/generate.py`](scripts/generate.py) — unified image generation dispatcher.
- [`markdown-converter`](https://github.com/) — paper ingestion via `uvx markitdown`.
