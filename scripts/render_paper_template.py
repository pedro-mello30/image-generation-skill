#!/usr/bin/env python3
"""
Starter scaffold for rendering a new paper's figures with the
``paper-to-image`` skill.

Step-by-step:
  1. Copy this file to ``scripts/render_<paper-slug>.py``.
  2. Replace the ``FIGURES`` list with one ``gen_*()`` function per figure
     in your paper's figure catalog.
  3. For each figure:
       - Pick the right template:
           * chat_mockup            → see ``demo_chat_mockup()`` below
           * architecture_diagram   → see ``demo_architecture_diagram()``
           * line_chart             → see ``demo_line_chart()``
       - Set ``PX_W, PX_H`` to the target image dimensions (in pixels).
         If you have a benchmark/reference image, match its dimensions
         exactly with:
              python3 -c "from PIL import Image; \\
                          print(Image.open('path/to/ref.png').size)"
       - Pull data values from the paper text first (tables / results
         sections); use visual estimation only as a last resort.
  4. Run from the project root:
              python3 scripts/render_<paper-slug>.py
     Outputs land in ``output/generated/<timestamp>-<slug>.png``.
"""
import matplotlib.pyplot as plt

from render_helpers import (
    DPI,
    BG, AI_BUB, AI_TC, USR_BUB, USR_TC, CODE_BG,
    RED_FG, GRN_FG, GRAY, LGRAY,
    CALL_TEL, FN_YEL, STR_GRN, OLD_RED, NEW_GRN,
    new_canvas, timestamp, save_pixel,
    bubble, alert_line, code_blk, search_blk,
    diagram_box, diagram_drum, uarrow, harrow, arc_arrow, context_brace,
)

TS = timestamp()


def out(slug: str) -> str:
    return f'output/generated/{TS}-{slug}.png'


# ─────────────────────────────────────────────────────────────────────────────
# Demo: chat_mockup
# ─────────────────────────────────────────────────────────────────────────────
def demo_chat_mockup():
    """Two-bubble chat with a single annotated code block."""
    PX_W, PX_H = 320, 160       # ← match your benchmark/reference dimensions
    fig, ax = new_canvas(PX_W, PX_H)

    ax.text(PX_W/2, 152, 'Date / heading', ha='center', va='center',
            color=GRAY, fontsize=7.5, zorder=3)

    # AI bubble (left, light gray, dark text)
    bubble(ax, 5, 118, 195, 26, AI_BUB,
           'Assistant message goes here.', tc=AI_TC, fs=7.5)

    # User bubble (right, blue, white text)
    bubble(ax, 90, 86, 220, 26, USR_BUB,
           'User reply goes here.', ha='center', fs=7.5)

    # Plain-text alert (no surrounding box)
    alert_line(ax, 70, 'System Alert: example event', RED_FG, fs=7)

    # Single-line code block with inline syntax highlighting
    code_blk(ax, 5, 38, PX_W-10, 22,
             [[('memory.append(',     FN_YEL),
               ('"example value")',   STR_GRN)]], fs=6.5)

    # Search-call block with paginated result lines
    search_blk(ax, 5, 4, PX_W-10, 30,
               call_parts=[('memory.search(', CALL_TEL),
                            ('"query"',        FN_YEL),
                            (')',              CALL_TEL)],
               hdr='Showing 1 of 1 results (page 1/1):',
               results=['"Example result row"'], fs=6.3)

    save_pixel(fig, out('chat_demo'))
    print(f'  ✓  {out("chat_demo")}')


# ─────────────────────────────────────────────────────────────────────────────
# Demo: architecture_diagram
# ─────────────────────────────────────────────────────────────────────────────
def demo_architecture_diagram():
    """Three components in a row with colored arrows."""
    PX_W, PX_H = 800, 320
    fig = plt.figure(figsize=(PX_W/DPI, PX_H/DPI))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PX_W);  ax.set_ylim(0, PX_H)
    ax.axis('off')

    # Optional title brace across the top of a logical group:
    context_brace(ax, 30, 540, 290, 'Logical Group Label', fs=12)

    # Boxes: diagram_box(ax, x, y, w, h, label, fc, tc, fw, fs, dashed)
    diagram_box(ax,  30, 160, 220, 110, 'Component\nA',
                fc='#1a1a1a', tc='white', fw='bold', fs=13)
    diagram_box(ax, 280, 160, 220, 110, 'Component\nB',
                fc='#f08c00', tc='#111', fw='bold', fs=13)
    diagram_box(ax, 530, 160, 220, 110, 'Component\nC',
                fc='white',   tc='#111', fw='bold', fs=13, dashed=True)

    # Storage drum (cylinder)
    diagram_drum(ax, 30, 20, 180, 110, 'Storage', fs=13)

    # Arrows
    uarrow(ax, 390, 130, 160, '#f08c00', lw=3.0)   # B (bottom) → B (top)
    harrow(ax, 250, 280, 215, '#333')              # A → B
    harrow(ax, 500, 530, 215, '#333')              # B → C
    arc_arrow(ax, 730, 215, 250, 215, '#4080c0',   # C → A (arc below)
              rad=-0.4)

    save_pixel(fig, out('arch_demo'), bg='white')
    print(f'  ✓  {out("arch_demo")}')


# ─────────────────────────────────────────────────────────────────────────────
# Demo: line_chart
# ─────────────────────────────────────────────────────────────────────────────
def demo_line_chart():
    """Multi-series accuracy vs X chart.

    ALWAYS extract data from the paper's tables/text first.
    Use visual estimation from a benchmark image only as a last resort.
    """
    X = [0, 1, 2, 3, 4]
    SERIES = [
        # (label, ys, color, linestyle, marker, markersize)
        ('Baseline A',   [0.40, 0.55, 0.65, 0.50, 0.30], '#1f77b4', '--', 's', 4),
        ('Baseline B',   [0.35, 0.45, 0.55, 0.40, 0.25], '#aec7e8', '-.', 'D', 4),
        ('Our Method',   [0.65, 0.68, 0.70, 0.69, 0.66], '#2ca02c', '-',  'o', 5),
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
    plt.savefig(out('line_chart_demo'), dpi=DPI, facecolor='white')
    plt.close(fig)
    print(f'  ✓  {out("line_chart_demo")}')


# ─────────────────────────────────────────────────────────────────────────────
# Register the figures you want to render
# ─────────────────────────────────────────────────────────────────────────────
FIGURES = [
    demo_chat_mockup,
    demo_architecture_diagram,
    demo_line_chart,
    # Add gen_figureN for each figure in your paper's catalog.
]


if __name__ == '__main__':
    print(f'Generating paper figures → output/generated/  [{TS}]')
    for gen in FIGURES:
        gen()
    print(f'Done — {len(FIGURES)} figure(s) saved.')
