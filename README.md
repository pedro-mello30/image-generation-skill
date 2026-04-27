# paper-to-image

A Cursor / Claude Code skill that reads a research paper and generates a publication-ready figure using your choice of image provider — Gemini, fal.ai, or Replit.

Built for researchers, engineers, and writers who want clean, paper-quality figures (LaTeX-style schematics, flow diagrams, positioning charts) — or a whiteboard-sketch alternate for talks and blogs — without writing TikZ or touching vector software.

## What it does

Hand it any paper source — arXiv URL, PDF path, `.docx`, HTML page, or pasted text — and it runs a five-stage pipeline:

```
Setup → Read paper → In-depth résumé → JSON prompt → Image
```

| Stage | Time | Output |
|-------|------|--------|
| **Setup (once)** | ~1 min | `config.json` with your chosen provider |
| **1. Read the paper** | ~1 min | `paper.md` — full text, ready to analyse |
| **2. In-depth résumé** | ~3–5 min | Problem, method, results, visual hooks |
| **3. Build JSON prompt** | ~2 min | `prompt.json` — `pipeline_configuration` validated by `json.loads` |
| **4. Draft render (1K)** | ~30 s | `output/…-draft.png` — fast iteration |
| **5. Final render (4K)** | ~1 min | `output/…-final.png` — publication-ready |

Every stage ends with an explicit ✋ stopping point so the workflow bails cleanly instead of burning a 4K render on a misaimed prompt.

## Output aesthetics

**Default — publication-ready paper figure**
Pure white background, rounded rectangle nodes, thin black strokes, labeled arrows, Computer Modern Serif typography. Looks like Figure 1 of a real paper.

**Alternate — whiteboard sketch**
Hand-drawn dry-erase markers, scientific charts with sticky-note annotations, research-office photography. For talks, blog posts, and social cards.

Switch between them by changing the style cues in `references/paper-figure-style.md` or `references/whiteboard-style.md`.

## Providers

Three providers are supported. Pick one at setup time; switch any time with `python scripts/setup.py`.

| Provider | Default model | Strengths | API key env var | Get key |
|----------|---------------|-----------|-----------------|---------|
| **Gemini** *(default)* | `gemini-3-pro-image-preview` | Best prompt adherence and text-in-image legibility; 1K / 2K / 4K; img2img | `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| **fal.ai** | `fal-ai/imagen4/preview` | Wide model catalogue (FLUX Pro, Imagen 4, FLUX Schnell); pay-per-use | `FAL_KEY` | [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys) |
| **Replit** | delegates to Gemini or fal | Run on Replit platform with keys stored in Replit Secrets | via Replit Secrets | Tools → Secrets in your Repl |

For per-provider model lists, error fixes, and `config.json` schema, see [`references/providers.md`](references/providers.md).

## Quickstart

```bash
# 1. Clone
git clone https://github.com/<your-username>/image-generation-skill.git
cd image-generation-skill

# 2. Set your API key (Gemini example)
export GEMINI_API_KEY=<your-key>

# 3. Configure provider (interactive, runs once)
python scripts/setup.py

# 4. Drop your paper in and run
uvx markitdown path/to/paper.pdf -o paper.md
# (agent reads paper.md, writes résumé, builds prompt.json)

# 5. Draft render
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename "output/$(date +%Y-%m-%d-%H-%M-%S)-draft.png" \
  --resolution 1K

# 6. Final render once prompt is locked
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename "output/$(date +%Y-%m-%d-%H-%M-%S)-final.png" \
  --resolution 4K
```

Override provider or model for a single run without changing config:

```bash
python scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename output/fal-test.png \
  --provider fal \
  --model fal-ai/flux/schnell \
  --resolution 1K
```

## Install

### Cursor — personal (available across all projects)

```bash
git clone https://github.com/<your-username>/image-generation-skill.git
mkdir -p ~/.cursor/skills/paper-to-image
cp image-generation-skill/SKILL.md ~/.cursor/skills/paper-to-image/
cp -r image-generation-skill/references ~/.cursor/skills/paper-to-image/
cp -r image-generation-skill/scripts ~/.cursor/skills/paper-to-image/
```

### Cursor — project-scoped (shared with anyone using the repo)

```bash
mkdir -p .cursor/skills/paper-to-image
cp image-generation-skill/SKILL.md .cursor/skills/paper-to-image/
cp -r image-generation-skill/references .cursor/skills/paper-to-image/
cp -r image-generation-skill/scripts .cursor/skills/paper-to-image/
```

### Claude Code

```bash
mkdir -p ~/.claude/skills/paper-to-image
cp image-generation-skill/SKILL.md ~/.claude/skills/paper-to-image/
cp -r image-generation-skill/references ~/.claude/skills/paper-to-image/
cp -r image-generation-skill/scripts ~/.claude/skills/paper-to-image/
```

Restart your editor. The skill triggers on phrases like:

- "make a figure for this paper"
- "generate a Figure 1 for arxiv.org/abs/…"
- "illustrate this paper" / "visualize this abstract"
- "draw a related-work positioning figure"
- "I need a system overview diagram for my method"
- "whiteboard sketch of the pipeline"

## Dependencies

| Dependency | Purpose | Install |
|------------|---------|---------|
| [`uv`](https://docs.astral.sh/uv/) | Runs provider scripts and auto-installs their Python deps | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `uvx markitdown` | Converts PDF / DOCX / HTML to Markdown | auto-fetched via `uvx`, no install needed |
| Python ≥ 3.10 | Runs `setup.py` and `generate.py` | system Python or `uv python install 3.12` |
| API key | Authenticates with your chosen provider | see [Providers](#providers) table above |

## File map

```
SKILL.md                              The workflow (setup + 4 steps). Read this first.
scripts/
  setup.py                            Interactive first-run provider setup. Writes config.json.
  generate.py                         Unified dispatcher: reads config.json, calls the right provider.
  providers/
    gemini.py                         Gemini 3 Pro Image backend.
    fal_ai.py                         fal.ai backend (FLUX Pro, Imagen 4, FLUX Schnell, etc.).
    replit.py                         Replit platform adapter (delegates to gemini or fal).
references/
  providers.md                        Provider setup, API keys, model lists, error fixes.
  nano-banana-prompt-shape.md         Canonical pipeline_configuration JSON skeleton + conventions.
  paper-figure-style.md               Default LaTeX paper-figure aesthetic. Style cues + full template.
  whiteboard-style.md                 Alternate whiteboard-sketch aesthetic for talks/blogs.
  figure-types.md                     Cheat sheet: paper claim → figure_type → layout pattern.
  img2img-preservation.md             Preservation rules for restyling existing images or sketches.
output/                               All generated PNGs land here. Gitignored (only .gitkeep tracked).
config.json                           Provider config written by setup.py. Gitignored (machine-specific).
README.md                             This file.
LICENSE                               MIT.
.gitignore                            Excludes output/*.png, config.json, prompt.json, paper.md, venvs.
```

## Customizing

| What to change | Where |
|----------------|-------|
| Default aesthetic (LaTeX paper figure) | `references/paper-figure-style.md` |
| Alternate aesthetic (whiteboard sketch) | `references/whiteboard-style.md` |
| Add a new aesthetic (blueprint, nature cover…) | Copy a style file, link it from `SKILL.md` Step 3 |
| Figure type catalogue | `references/figure-types.md` |
| Prompt JSON shape | `references/nano-banana-prompt-shape.md` |
| Img2img preservation rules | `references/img2img-preservation.md` |
| Provider or model | `python scripts/setup.py` or edit `config.json` |
| Pipeline steps / stopping points | `SKILL.md` |

## Design principles

1. **Paper-grounded, not generic.** Every visual element traces back to a hook in the paper résumé. No model-invented labels, no decorative content.
2. **Provider-agnostic.** Gemini, fal.ai, and Replit are supported today; adding a new provider is one new file in `scripts/providers/`.
3. **Iterate at 1K, escalate to 4K.** The bottleneck is prompt-locking, not resolution. Cheap drafts catch failures early.
4. **Honest about typography.** Diffusion models still mangle long labels and equations. The skill names this explicitly and points to TikZ / matplotlib / mermaid as the right tool when text fidelity is critical.
5. **Two aesthetics, one shape.** Paper-figure default; whiteboard alternate. Same JSON shape, different style cues. Switching is a one-file change.
6. **Validate before render.** `json.loads` the prompt locally before paying for an API call.
7. **Stopping points, not shame.** Each step ends with ✋ "stop here unless…" so the workflow bails cleanly instead of burning a 4K render on a misaimed prompt.
8. **Explicit labels over invented ones.** Every visible word is listed verbatim in `weighted_positive`. The model honors quoted strings far better than implied ones.

## Caveats

- Built and tested with Cursor (Composer) and Claude Code. Should work with any agent runtime that loads Markdown skills with YAML frontmatter.
- Gemini 3 Pro Image's text rendering is better than older diffusion models, but still imperfect. Expect 2–4 retries on labels with five or more words.
- 4K renders are large (5–18 MB PNGs) and take ~45 s each. The skill defaults to 1K for iteration to save time and quota.
- For figures where typography must be exact (equations with subscripts, strict author-style guides), use TikZ or matplotlib instead. The skill recommends this fallback explicitly in Step 3.
- The whiteboard aesthetic suits talks and blogs but not paper bodies. Default stays paper-figure for a reason.
- fal.ai's `fal-ai/flux/schnell` is fast and cheap for rapid iteration but has a lower quality ceiling than Imagen 4 or FLUX Pro. Use it for 1K drafts only.

## Contributing

Issues and PRs welcome. Especially interested in:

- New provider backends in `scripts/providers/` (e.g. OpenAI Images API, Stability AI, Replicate).
- Additional `figure_type` patterns (`box_plot`, `forest_plot`, `architecture_table`).
- Domain-adapted style references (`nature-style.md`, `blueprint-style.md`, `ieee-style.md`).
- Edge cases where Step 3 produces invalid JSON or a 4K render persistently mangles labels — paste the paper excerpt + résumé + JSON.

## License

MIT — see [LICENSE](LICENSE).

## Credits

- Image generation: [Gemini 3 Pro Image](https://deepmind.google/), [fal.ai](https://fal.ai/).
- Paper ingestion: [microsoft/markitdown](https://github.com/microsoft/markitdown).
- Skill format: [Anthropic Claude Skills](https://www.anthropic.com/news/claude-skills) and [Cursor Agent Skills](https://cursor.com/docs/agent/skills).
- Repo layout inspired by [iagomsouza/adhd-paper-reader](https://github.com/iagomsouza/adhd-paper-reader).
