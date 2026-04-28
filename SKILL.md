---
name: paper-to-image
description: Turn any research paper (PDF, arXiv URL, .docx, HTML, .tex export) into publication-ready figures via a 5-step pipeline — read the paper, write an in-depth résumé with a figure catalog, choose a render path (code for charts/diagrams/chat UIs; Nano Banana JSON for conceptual art), then generate PNGs. Handles three figure archetypes found in systems/ML papers: chat-UI mockups, architecture diagrams, and performance charts. Default output looks like the actual figures inside a real paper. Use when the user asks for paper figures, diagrams, schematics, system overviews, result charts, or illustrated conversation examples from a paper, abstract, or scientific PDF.
---

# Paper → Summary → Figure Plan → Code or Prompt → PNG

A generic, paper-agnostic pipeline. Five sequential steps. Do not skip any. Each step's output feeds the next.

```
Paper ──▶ Markdown text ──▶ In-depth résumé + figure catalog
       ──▶ Render-path routing (code vs Nano Banana)
       ──▶ Python script or JSON prompt
       ──▶ PNG in output/generated/
```

The skill ships with a **worked reference implementation** (the MemGPT paper, all 8 figures) under `scripts/render_all_memgpt.py`. Treat it as a calibration target — once you can reproduce its figures, the same primitives produce comparable figures for any other systems/ML paper.

## Project layout

```
input/                          ← drop the source paper(s) here
output/
  benchmark/                    ← (optional) reference figures to match exactly
  generated/                    ← timestamped renders end up here
scripts/
  render_helpers.py             ← shared palette + drawing primitives (import these)
  render_paper_template.py      ← starter scaffold for a NEW paper
  render_all_memgpt.py          ← worked reference example
  setup.py / generate.py        ← provider config + Nano Banana dispatcher
SKILL.md                        ← this file
```

## First-run setup

Check if the provider is configured:

```bash
test -f config.json && python3 -c "import json; c=json.load(open('config.json')); print('Provider:', c['provider'], '|', 'Model:', c.get('model','n/a'))" || echo "Not configured"
```

If not configured — or if the user wants to change provider — run the interactive setup:

```bash
python3 scripts/setup.py
```

This asks:
1. Which provider: **Gemini** (default), **fal.ai**, or **Replit** platform.
2. Which model within that provider.
3. Checks whether the required API key env var is set.

Writes `config.json` (gitignored). All subsequent renders read from it automatically.

See [`references/providers.md`](references/providers.md) for API key setup, model lists, and per-provider caveats.

✋ **Stop here if** the provider is not yet configured **and** the paper has any `nano-banana` figures. Code-rendered figures don't need a provider.

## Workflow checklist

Copy this checklist into the chat and tick items as you progress:

```
- [ ] Setup: provider configured (only needed for nano-banana figures)
- [ ] Step 1: Read the paper (convert to Markdown)
- [ ] Step 2: Write in-depth résumé + figure catalog
- [ ] Step 3: Choose render path for each figure
- [ ] Step 4a (code path): Write & run Python script
- [ ] Step 4b (Nano Banana path): Build JSON prompt and validate
- [ ] Step 5: Generate / save to output/generated/
- [ ] (Optional) Compare to output/benchmark/ and iterate
```

---

## Step 1 — Read the paper

Convert any source to Markdown so the full text is available. Use `uvx markitdown` or `pdftotext`.

```bash
uvx markitdown input/<paper>.pdf -o input/<paper>.md
# or
pdftotext input/<paper>.pdf input/<paper>.txt
```

Notes:

- Works for PDF, .docx, .pptx, HTML, EPub, and more.
- For arXiv links, prefer the PDF URL (`https://arxiv.org/pdf/<id>.pdf`).
- For scanned PDFs, re-run with Azure Document Intelligence (`-d -e ENDPOINT`).
- Read the resulting `.md` / `.txt` before continuing.

✋ **Stop here if** the paper text is too short (< 500 words) or you cannot extract clean text.

---

## Step 2 — In-depth résumé + figure catalog

Write the résumé directly in chat (or save to `summary.md`). Use this outline:

```markdown
# <Paper title> — In-depth résumé

## Problem & motivation
What gap or question the paper addresses and why it matters.

## Method
Core technique, architecture, formalism, or experimental design. Include
notable equations, diagrams, or pseudocode the paper relies on.

## Key results
Quantitative findings, tables, headline numbers, ablations.
**Extract exact numbers from tables and result sections** — these will feed
chart figures directly.

## Limitations & open questions
Failure modes, caveats, and what the authors flag as future work.

## Visual hooks
3–5 concrete image-able concepts from the paper.

## Figure catalog
For every figure in the paper, list one entry:

| # | Description | Type | Render path | Notes |
|---|-------------|------|-------------|-------|
| 1 | <what the figure shows> | <type — see table below> | code \| nano-banana | dimensions, key colors, key labels |
```

Figure types and their render paths:

| Type                 | When to use                                      | Render path  |
|----------------------|--------------------------------------------------|--------------|
| chat_mockup          | Annotated chat/conversation UI screenshots      | **code**     |
| architecture_diagram | System block diagrams with colored components   | **code**     |
| line_chart           | Multi-line accuracy/loss vs X-axis plots        | **code**     |
| bar_chart            | Category comparisons on one metric              | **code**     |
| scatter_plot         | Point clouds with labeled axes                  | **code**     |
| schematic_flow       | Pipeline box-and-arrow (few nodes, B&W LaTeX)   | nano-banana  |
| conceptual           | Metaphor, cover art, concept illustration       | nano-banana  |
| venn / quadrant      | Positioning vs prior work                       | nano-banana  |

✋ **Stop here if** you cannot find at least one concrete visual hook. A weak hook produces a generic image; ask the user which aspect of the paper they want illustrated.

---

## Step 3 — Choose render path

For each figure in the catalog, pick a path:

- **Code path** (`chat_mockup`, `architecture_diagram`, `line_chart`, `bar_chart`, `scatter_plot`) — write a Python script using `matplotlib` and run it directly. Always faster, always typographically exact.
- **Nano Banana path** (`schematic_flow`, `conceptual`, `venn`, `quadrant`) — build the JSON prompt and use `scripts/generate.py`.

When in doubt, prefer the **code path**. Diffusion models (including Gemini 3 Pro Image) frequently mangle long labels, made-up acronyms, and equations. Code is exact.

---

## Step 4a — Code-rendered figures (preferred for charts, diagrams, chat UIs)

### Quickstart for a new paper

1. Copy the starter scaffold:
   ```bash
   cp scripts/render_paper_template.py scripts/render_<paper-slug>.py
   ```
2. Replace the `demo_*` functions with `gen_figure1()`, `gen_figure2()`, … one per figure in your catalog.
3. For each figure: pick the matching template below, set `PX_W`/`PX_H`, plug in your data/labels.
4. Run:
   ```bash
   python3 scripts/render_<paper-slug>.py
   ```
   Outputs land in `output/generated/<timestamp>-<slug>.png`.

### Shared helpers

All three templates draw from `scripts/render_helpers.py`. Import what you need:

```python
from render_helpers import (
    DPI,
    BG, AI_BUB, AI_TC, USR_BUB, USR_TC, CODE_BG,
    RED_FG, GRN_FG, GRAY, LGRAY,
    CALL_TEL, FN_YEL, STR_GRN, OLD_RED, NEW_GRN,
    new_canvas, timestamp, save_pixel,
    bubble, alert_line, code_blk, search_blk,
    diagram_box, diagram_drum, uarrow, harrow, arc_arrow, context_brace,
)
```

**Why these helpers exist:** `matplotlib`'s `FancyBboxPatch` expands outward by `pad` on every side, so the box you draw isn't the box you specified. The `rbox()` helper inside `render_helpers.py` compensates for this so you get **pixel-exact placement**. All other primitives build on top of `rbox()`.

### Pixel-based coordinate convention

- `DPI = 100`, so `figsize = (PX_W/DPI, PX_H/DPI)` ⟹ **1 data unit = 1 pixel**.
- `new_canvas(PX_W, PX_H)` returns a full-bleed `(fig, ax)` with no margins; `ax.set_xlim(0, PX_W)`, `ax.set_ylim(0, PX_H)`.
- Y axis goes **upward**: `y=0` is bottom, `y=PX_H` is top. Stack chat bubbles top-down by decreasing `y` for each new element.
- Match `PX_W`/`PX_H` to your benchmark exactly:
  ```bash
  python3 -c "from PIL import Image; print(Image.open('output/benchmark/figure_X.png').size)"
  ```

---

### Template A — `chat_mockup` (white-background conversation with code blocks)

Used for figures that show an LLM chatting with a user, often interspersed with system-alert lines and annotated code/search calls. Light-gray AI bubbles with dark text on the left; blue user bubbles with white text on the right; dark navy code/search blocks for syntax-highlighted snippets.

```python
import matplotlib.pyplot as plt
from render_helpers import (
    BG, AI_BUB, AI_TC, USR_BUB, GRAY, RED_FG,
    CALL_TEL, FN_YEL, STR_GRN,
    new_canvas, timestamp, save_pixel,
    bubble, alert_line, code_blk, search_blk,
)

PX_W, PX_H = 320, 170                # ← match target/benchmark dimensions
fig, ax = new_canvas(PX_W, PX_H)

ax.text(PX_W/2, PX_H-10, 'February 7', ha='center', va='center',
        color=GRAY, fontsize=7.5, zorder=3)

# AI (left, light gray + dark text)
bubble(ax, 5, 130, 195, 26, AI_BUB,
       'Assistant message goes here.', tc=AI_TC, fs=7.5)

# User (right, blue + white text — default tc)
bubble(ax, 90, 98, 220, 26, USR_BUB,
       'User reply goes here.', ha='center', fs=7.5)

# Plain-text alert (no surrounding box)
alert_line(ax, 80, 'System Alert: example event', RED_FG, fs=7)

# Single-line code block, syntax-highlighted
code_blk(ax, 5, 50, PX_W-10, 22,
         [[('memory.append(',   FN_YEL),
           ('"example value")', STR_GRN)]], fs=6.5)

# Search call + paginated results
search_blk(ax, 5, 8, PX_W-10, 38,
           call_parts=[('memory.search(', CALL_TEL),
                        ('"query"',        FN_YEL),
                        (')',              CALL_TEL)],
           hdr='Showing 1 of 1 results (page 1/1):',
           results=['"Example result row"'], fs=6.3)

save_pixel(fig, f'output/generated/{timestamp()}-chat.png')
```

**Patterns to remember**
- **AI bubble**: `bubble(ax, 5, y, ~195, 26..30, AI_BUB, text, tc=AI_TC)`.
- **User bubble**: `bubble(ax, ~90, y, ~215, 26..30, USR_BUB, text, ha='center')`.
- **Alert line**: `alert_line(ax, y, text, RED_FG)` for errors/pressure; `GRN_FG` for success.
- **Inline code**: `code_blk(ax, x, y, w, h, [[(fn, FN_YEL), (str, STR_GRN)]])`.
- **Multi-line edit (e.g. `replace()`)**: pass multiple lines, use `OLD_RED`/`NEW_GRN`.
- **Search call**: `call_parts = [(fn, CALL_TEL), (term, FN_YEL), (')', CALL_TEL)]`.
- **Line height** in code/search blocks: `(h - 8) / n_lines` ≈ 11–13 px at fs=6.5.

---

### Template B — `architecture_diagram` (colored boxes with arrows)

Used for system architecture figures with named components, data-flow arrows, optional storage cylinders, and labeled tiers.

```python
import matplotlib.pyplot as plt
from render_helpers import (
    DPI, timestamp, save_pixel,
    diagram_box, diagram_drum,
    uarrow, harrow, arc_arrow, context_brace,
)

PX_W, PX_H = 800, 320
fig = plt.figure(figsize=(PX_W/DPI, PX_H/DPI))
fig.patch.set_facecolor('white')
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, PX_W);  ax.set_ylim(0, PX_H);  ax.axis('off')

# Optional grouping label (overbrace)
context_brace(ax, 30, 540, 290, 'Logical Group Label', fs=12)

# Component boxes — fc/tc/fw/fs are per-component
diagram_box(ax,  30, 160, 220, 110, 'Component\nA',
            fc='#1a1a1a', tc='white', fw='bold', fs=13)
diagram_box(ax, 280, 160, 220, 110, 'Component\nB',
            fc='#f08c00', tc='#111', fw='bold', fs=13)
diagram_box(ax, 530, 160, 220, 110, 'Component\nC',
            fc='white',   tc='#111', fw='bold', fs=13, dashed=True)

# Storage cylinder
diagram_drum(ax, 30, 20, 180, 110, 'Storage', fs=13)

# Arrows: choose by type
uarrow(ax, 390, 130, 160, '#f08c00', lw=3.0)        # vertical UP
harrow(ax, 250, 280, 215, '#333')                    # horizontal →
arc_arrow(ax, 730, 215, 250, 215, '#4080c0',         # curved ↻
          rad=-0.4)

# Optional dashed bounding rectangle around a logical group
ax.add_patch(plt.Rectangle((25, 155), 480, 120,
    fill=False, ec='black', lw=1.3, ls='--', zorder=1))

save_pixel(fig, f'output/generated/{timestamp()}-arch.png', bg='white')
```

**Patterns to remember**
- **Box colors**: each component gets `(fc, tc, fw)`. Pick a consistent palette per paper — fill colors usually carry semantic meaning (e.g. read-only vs read-write).
- **Drum (storage cylinder)**: `diagram_drum()` for any persistent store / database.
- **Vertical UP arrow**: `uarrow(ax, x, y_bottom, y_top, color, lw)`.
- **Horizontal arrow**: `harrow(ax, x0, x1, y, color)`. For bidirectional, draw two parallel arrows offset by ~10–20 px.
- **Curved arc**: `arc_arrow(...)` — negative `rad` curves below the straight line, positive above. Useful for long-range connections that would cross other elements.
- **Dashed grouping rectangle**: `plt.Rectangle((x, y), w, h, fill=False, ls='--', ec='black', lw=1.3)` for "this set of boxes belongs together" semantics.
- **Top brace + label**: `context_brace()` gives the LaTeX-`\overbrace` look common in systems papers.

---

### Template C — `line_chart` (accuracy vs X-axis, multiple models)

Used for performance result figures comparing multiple models across a scalar axis (documents retrieved, nesting level, epoch, etc.).

**Critical — extract data from the paper text first.**
1. **Tables**: exact accuracy/F1/ROUGE numbers usually live in tables — copy them verbatim.
2. **Results prose**: the paper's narrative tells you the **shape** of each curve (monotonic? rises-then-falls? plateaus?). Always reread it before plotting.
3. **Visual estimation from a benchmark image**: last resort only — small charts make it easy to mis-read by ±0.05 absolute accuracy.

> Real-world example: in MemGPT Figure 5, fixed-context baselines (GPT-4, GPT-3.5) RISE then FALL as documents fill the context window — *not* monotonically decrease. Reading the paper text avoids this kind of mistake.

```python
import matplotlib.pyplot as plt
from render_helpers import DPI, timestamp

X = [0, 1, 2, 3, 4]
SERIES = [
    # (label,         ys,                              color,    ls,    marker, ms)
    ('Baseline A',    [0.40, 0.55, 0.65, 0.50, 0.30], '#1f77b4', '--', 's', 4),
    ('Baseline B',    [0.35, 0.45, 0.55, 0.40, 0.25], '#aec7e8', '-.', 'D', 4),
    ('Our Method',    [0.65, 0.68, 0.70, 0.69, 0.66], '#2ca02c', '-',  'o', 5),
]

fig, ax = plt.subplots(figsize=(3.5, 2.3))
fig.patch.set_facecolor('white');  ax.set_facecolor('white')
for label, ys, color, ls, marker, ms in SERIES:
    ax.plot(X, ys, color=color, linestyle=ls, marker=marker,
            markersize=ms, linewidth=1.2, label=label)
ax.set_xlabel('X-axis label', fontsize=8)
ax.set_ylabel('Accuracy',     fontsize=8)
ax.set_ylim(0.0, 0.8)
ax.grid(True, linestyle='-', linewidth=0.3, color='#e0e0e0', zorder=0)
ax.tick_params(labelsize=7)
ax.legend(fontsize=6, loc='lower left', framealpha=0.95,
          handlelength=2.2, handletextpad=0.5)
for spine in ax.spines.values():
    spine.set_linewidth(0.6);  spine.set_color('#bbb')
plt.tight_layout(pad=0.3)
plt.savefig(f'output/generated/{timestamp()}-chart.png',
            dpi=DPI, facecolor='white')
plt.close(fig)
```

**Patterns to remember**
- **Color palette**: stay close to matplotlib's defaults (`#1f77b4`, `#ff7f0e`, `#2ca02c`, …) — papers tend to use these.
- **Line style mapping**: solid for "ours" / hero method; dashed/dotted for baselines. Distinct **markers** also help when colors print B&W.
- **Y-limits**: trim aggressively. Don't waste vertical space on `(0, 1)` when results live in `(0.05, 0.75)`.
- **Tiny figures**: when matching a benchmark thumbnail (e.g. 320×210 px), use `figsize=(PX_W/100, PX_H/100)` and shrink `fontsize` to 6–8.
- **Bar charts**: same approach with `ax.bar()` + hatch patterns instead of markers.

---

## Step 4b — Nano Banana JSON prompt (for conceptual / organic figures)

Use this path only for `schematic_flow`, `conceptual`, `venn`, and `quadrant` figures that are difficult to express in code.

Read these references before drafting:

- [`references/nano-banana-prompt-shape.md`](references/nano-banana-prompt-shape.md) — canonical JSON skeleton.
- [`references/paper-figure-style.md`](references/paper-figure-style.md) — default LaTeX-style cues.
- [`references/figure-types.md`](references/figure-types.md) — figure-type cheat sheet.
- [`references/whiteboard-style.md`](references/whiteboard-style.md) — alternate hand-drawn template.

**Default aesthetic: publication-ready paper figure.** Clean black-on-white schematic, rounded rectangle nodes, thin strokes, labeled arrows, Computer Modern Serif typography.

**Text-rendering reality check.** Diffusion models mangle long labels and equations:

- Keep every label 1–4 real English words.
- At most one boxed equation per figure.
- Re-render 2–4 times; tweak the offending label as a separate `weighted_positive` line.

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

Save and validate:

```bash
cat > prompt.json <<'JSON'
{ "pipeline_configuration": { ... } }
JSON
python3 -c "import json; json.load(open('prompt.json')); print('valid')"
```

✋ **Stop here unless** `json.load` returns `valid`.

---

## Step 5 — Generate the image

### Code-path figures

```bash
python3 scripts/render_<paper-slug>.py
```

The script saves directly to `output/generated/<timestamp>-<slug>.png`. No additional step needed.

### Nano Banana figures

Draft (txt2img):

```bash
python3 scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename "output/generated/$(date +%Y-%m-%d-%H-%M-%S)-paper-draft.png" \
  --resolution 1K
```

✋ **Stop here unless** the 1K draft is on-target. Only escalate to 4K once the draft is right.

Final (4K):

```bash
python3 scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename "output/generated/$(date +%Y-%m-%d-%H-%M-%S)-paper-final.png" \
  --resolution 4K
```

Img2img (when a reference image is provided):

```bash
python3 scripts/generate.py \
  --prompt "$(cat prompt.json)" \
  --filename "output/generated/$(date +%Y-%m-%d-%H-%M-%S)-paper-edit.png" \
  --input-image path/to/reference.png \
  --resolution 2K
```

Always run from the project root so `output/` resolves correctly.

---

## Calibration loop (when a benchmark exists)

If the user supplies reference images in `output/benchmark/`, treat them as the visual target:

1. Match `PX_W`/`PX_H` exactly with `Image.open(...).size`.
2. Generate the figure.
3. Open both images side-by-side. Compare:
   - Element positions (AI bubble height, code block width, …).
   - Color values (especially bubble fills, code highlight colors).
   - Text content (typos, formatting, line breaks).
   - Arrow targets (which box does each arrow connect to?).
   - Chart data (does each series have the right shape per the paper text?).
4. Fix one thing at a time, regenerate, re-compare.

The MemGPT reference (`scripts/render_all_memgpt.py` ↔ `output/benchmark/figure_*.png`) shows what "matches benchmark" looks like in practice.

---

## Worked reference example — MemGPT paper

The MemGPT paper ("Towards LLMs as Operating Systems", arXiv 2310.08560) demonstrates all three figure archetypes. Use this as a calibration target — once you can reproduce its 8 figures from `output/benchmark/`, the same primitives work for any other paper.

### Paper in brief
MemGPT treats the LLM as an OS: it moves data between a fixed-size **main context** (the LLM's context window) and unbounded **external storage** (recall + archival). A Function Executor and Queue Manager handle paging, similar to virtual memory.

### Figure catalog (MemGPT)

| # | File | Description | Type | Render |
|---|------|-------------|------|--------|
| 1 | `output/benchmark/figure.png`   | Birthday chat, memory-pressure alert, `working_context.append()` | `chat_mockup` | code |
| 2 | `output/benchmark/figure_2.png` | "Six flags" recall search with paginated results | `chat_mockup` | code |
| 3 | `output/benchmark/figure_3.png` | Full system architecture: context window tiers + external storage | `architecture_diagram` | code |
| 4 | `output/benchmark/figure_4.png` | Feb 14 breakup, `working_context.replace()` | `chat_mockup` | code |
| 5 | `output/benchmark/figure_5.png` | DMR accuracy vs documents retrieved (5 model lines) | `line_chart` | code |
| 6 | `output/benchmark/figure_6.png` | Nobel Prize archival storage search, paginated | `chat_mockup` | code |
| 7 | `output/benchmark/figure_7.png` | Multi-session chat accuracy vs nesting level | `line_chart` | code |
| 8 | `output/benchmark/figure_8.png` | Key-value store search through archival storage | `chat_mockup` | code |

Reproduce all 8 figures with:

```bash
python3 scripts/render_all_memgpt.py
```

### Chat mockup colour values (verified against `output/benchmark/`)

Chat figures use a **white page background**. Code/search blocks retain a dark navy background for contrast.

| Element                          | Hex       | Notes |
|----------------------------------|-----------|-------|
| Page background                  | `#ffffff` | White |
| AI bubble (left)                 | `#e5e5ea` | iOS light gray; pair with `tc=AI_TC` |
| AI bubble text                   | `#1c1c1e` | Dark, readable on light gray |
| User bubble (right)              | `#1a6bcd` | Blue; pair with white text |
| Code/search block background     | `#1a1a2e` | Dark navy |
| System alert text (memory)       | `#ff3b30` | Plain text, NO box |
| System alert text (archive done) | `#30d158` | Plain text, NO box |
| Function name in search calls    | `#4ec9b0` | Teal `CALL_TEL` |
| Search term / string literals    | `#dcdcaa` | Yellow `FN_YEL` |
| Code block string literals       | `#4ec9b0` | Teal `STR_GRN` |
| Old value in `replace()`         | `#f44747` | |
| New value in `replace()`         | `#4ec9b0` | |
| Result body text                 | `#c8c8d8` | |
| Date header                      | `#8888aa` | |

### Architecture diagram (Figure 3) — verified arrow pattern

- **Orange UP**: Function Executor → Working Context.
- **Pink UP**: Queue Manager → FIFO Queue (left position).
- **Blue UP**: Queue Manager → FIFO Queue (right position, slight offset). Two arrows to FIFO Queue.
- **Green bidirectional** (horizontal): Archival Storage ↔ Function Executor.
- **Black bidirectional** (horizontal): Function Executor ↔ Queue Manager.
- **Blue ONE-WAY right** (horizontal): Queue Manager → Recall Storage (Write via Queue Manager).
- **Large blue arc** (curved, below): Recall Storage → Function Executor (Read via Functions).
- **Dashed bounding rectangle**: around the 3 Prompt-Tokens boxes (System Instructions + Working Context + FIFO Queue), NOT around Output Buffer. Output Buffer has its own separate dashed border.

### Line charts (Figures 5 & 7) — values

These were extracted from the paper's tables and prose, then cross-checked against the benchmark image:

- **Figure 5 (Document QA)**: fixed-context models RISE then FALL as documents fill the 8k window; MemGPT (GPT-4 / GPT-4 Turbo) stays flat ~0.67. GPT-4 series: `[0.40, 0.60, 0.70, 0.60, 0.38, 0.28, 0.20, 0.14, 0.10]` over `X = [0, 25, 50, 75, 100, 125, 150, 175, 200]`.
- **Figure 7 (Nested KV)**: MemGPT (GPT-4 Turbo) plateaus at 1.0 for levels 0–1 then degrades; baselines drop to ~0 by level 3. The paper notes that *"MemGPT with GPT-4 Turbo performs worse than MemGPT with GPT-4"*, so MemGPT (GPT-4) holds up better at higher nesting.

Always cross-check chart shapes against the paper's *Results* section before committing data values.

---

## API keys

Keys are read from environment variables — never stored in any committed file.

| Provider | Env var | Get key at |
|----------|---------|------------|
| Gemini | `GEMINI_API_KEY` | https://aistudio.google.com/apikey |
| fal.ai | `FAL_KEY` | https://fal.ai/dashboard/keys |

Add to your shell profile:

```bash
export GEMINI_API_KEY=<your-key>
export FAL_KEY=<your-key>
```

If the user pasted a key in chat, treat it as compromised — ask them to rotate it.

See [`references/providers.md`](references/providers.md) for full setup, model options, and common error fixes.

---

## Iteration tips

- Keep Python render scripts; tweak one parameter at a time between runs.
- One change per iteration so cause and effect are clear.
- For code-path figures: each run produces a new timestamped file — no overwrites.
- For Nano Banana figures: if a label renders garbled, simplify it or move it to the caption.
- When in doubt about a chart shape, **reread the paper's results section** before tweaking pixels.

## Resources

- [`scripts/render_helpers.py`](scripts/render_helpers.py) — palette + drawing primitives (import these into every render script).
- [`scripts/render_paper_template.py`](scripts/render_paper_template.py) — starter scaffold for a new paper.
- [`scripts/render_all_memgpt.py`](scripts/render_all_memgpt.py) — worked reference example (all 8 MemGPT figures).
- [`scripts/setup.py`](scripts/setup.py) — interactive provider setup (Nano Banana only).
- [`scripts/generate.py`](scripts/generate.py) — unified Nano Banana dispatcher.
- [`references/providers.md`](references/providers.md) — provider setup, API keys, model lists.
- [`references/nano-banana-prompt-shape.md`](references/nano-banana-prompt-shape.md) — JSON skeleton.
- [`references/paper-figure-style.md`](references/paper-figure-style.md) — LaTeX paper-figure aesthetic.
- [`references/whiteboard-style.md`](references/whiteboard-style.md) — whiteboard-sketch aesthetic.
- [`references/figure-types.md`](references/figure-types.md) — figure-type cheat sheet.
- [`references/img2img-preservation.md`](references/img2img-preservation.md) — img2img preservation rules.
