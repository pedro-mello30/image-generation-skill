"""
Shared rendering primitives for the paper-to-image skill.

Generic, paper-agnostic helpers for the three code-rendered figure archetypes:
  • chat_mockup        — bubbles + alerts + inline code/search blocks
  • architecture_diagram — boxes, drums (cylinders), and colored arrows
  • line_chart         — multi-series accuracy/loss vs X-axis

Design principles
─────────────────
1. **1 data unit = 1 pixel** (DPI=100). Set PX_W / PX_H equal to the target
   image's pixel dimensions (e.g. matching a benchmark reference). Elements
   stack from top (y=PX_H) toward bottom (y=0).
2. ``rbox()`` compensates for ``FancyBboxPatch``'s outward ``pad`` expansion
   so the visible outer boundary equals (x, y, x+w, y+h) you specified.
3. Inline coloring (``render_inline``) lays out ``[(text, color), ...]``
   segments at consecutive x positions — used for syntax highlighting in
   code/search blocks.
"""
from __future__ import annotations

import os
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

DPI = 100   # 1 data unit = 1 pixel at DPI=100

# ── Palette: chat-mockup figures (white background) ──────────────────────────
BG       = '#ffffff'   # page background
AI_BUB   = '#e5e5ea'  # left (assistant) bubble — iOS light gray
AI_TC    = '#1c1c1e'  # text inside AI bubble (dark)
USR_BUB  = '#1a6bcd'  # right (user) bubble — blue
USR_TC   = '#ffffff'  # text inside user bubble (white)
CODE_BG  = '#1a1a2e'  # code/search block background (dark navy)
RED_FG   = '#ff3b30'  # error / pressure alert text
GRN_FG   = '#30d158'  # success alert text
GRAY     = '#8888aa'  # date header / muted label
LGRAY    = '#8899bb'  # results-header dim text
RES_TXT  = '#c8c8d8'  # result body text

# Syntax-highlighting colors (used inside code_blk / search_blk):
CALL_TEL = '#4ec9b0'  # function name (teal)
FN_YEL   = '#dcdcaa'  # search term / string literal (yellow)
STR_GRN  = '#4ec9b0'  # string literal in code blocks (teal)
OLD_RED  = '#f44747'  # old value in replace()-style edits
NEW_GRN  = '#4ec9b0'  # new value in replace()-style edits


# ─────────────────────────────────────────────────────────────────────────────
# Canvas + I/O
# ─────────────────────────────────────────────────────────────────────────────
def new_canvas(px_w: int, px_h: int, bg: str = BG):
    """Create a (px_w × px_h) figure with no margins; 1 data unit = 1 pixel."""
    fig = plt.figure(figsize=(px_w / DPI, px_h / DPI))
    fig.patch.set_facecolor(bg)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(bg)
    ax.set_xlim(0, px_w)
    ax.set_ylim(0, px_h)
    ax.axis('off')
    return fig, ax


# Backwards-compatible alias used by render_all_memgpt.py
def new_chat(px_w: int, px_h: int):
    return new_canvas(px_w, px_h, bg=BG)


def timestamp() -> str:
    """``YYYY-MM-DD-HH-MM-SS`` for output filenames."""
    return datetime.now().strftime('%Y-%m-%d-%H-%M-%S')


def save_pixel(fig, path: str, bg: str = BG):
    """Save a pixel-perfect canvas figure (no auto-cropping, no margins)."""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    plt.savefig(path, dpi=DPI, bbox_inches=None, pad_inches=0, facecolor=bg)
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Geometry primitives
# ─────────────────────────────────────────────────────────────────────────────
def rbox(ax, x, y, w, h, fc, *,
         pad: float = 4, ec: str = 'none', lw: float = 0,
         ls='solid', zorder: int = 2):
    """Rounded box whose VISIBLE outer boundary equals (x, y, x+w, y+h).

    ``FancyBboxPatch`` expands outward by ``pad`` on every side. We shrink the
    inner rectangle by ``pad`` so the on-screen result matches what you asked
    for. Use this whenever pixel-precise placement matters.
    """
    ax.add_patch(FancyBboxPatch(
        (x + pad, y + pad), max(w - 2 * pad, 1), max(h - 2 * pad, 1),
        boxstyle=f"round,pad={pad}", fc=fc, ec=ec, lw=lw, ls=ls, zorder=zorder))


def cw(fs: float) -> float:
    """Estimated monospace character width in pixels at font-size ``fs`` (pt)."""
    return 0.56 * fs * DPI / 72


# ─────────────────────────────────────────────────────────────────────────────
# Chat-mockup primitives
# ─────────────────────────────────────────────────────────────────────────────
def bubble(ax, x, y, w, h, color, text, *,
           ha: str = 'left', fs: float = 7.5, tc: str = USR_TC):
    """A single chat bubble.

    For AI/assistant bubbles use ``color=AI_BUB, tc=AI_TC`` (dark text on
    light gray). For user bubbles use ``color=USR_BUB`` and the default
    white text.
    """
    rbox(ax, x, y, w, h, color, pad=5)
    tx = x + 9 if ha == 'left' else x + w / 2
    ax.text(tx, y + h / 2, text, va='center', ha=ha, color=tc,
            fontsize=fs, linespacing=1.2, zorder=3)


def alert_line(ax, y, text, color, *, fs: float = 7.0, x: float = 8):
    """Plain-text alert line (no surrounding box), bold, left-aligned."""
    ax.text(x, y, text, va='center', ha='left',
            color=color, fontsize=fs, fontweight='bold', zorder=3)


def render_inline(ax, x_start, y, parts, fs: float):
    """Render ``[(text, color), ...]`` segments at consecutive x positions.

    Used internally by ``code_blk`` and ``search_blk`` to syntax-highlight a
    single line by drawing each colored segment immediately after the last.
    """
    x = x_start
    for txt, col in parts:
        ax.text(x, y, txt, va='center', ha='left', color=col,
                fontsize=fs, fontfamily='monospace', zorder=3)
        x += len(txt) * cw(fs)


def code_blk(ax, x, y, w, h, lines_parts, *, fs: float = 6.5):
    """Multi-line code block on the dark ``CODE_BG`` background.

    ``lines_parts`` is a list of lines, where each line is itself a list of
    ``(text, color)`` segments rendered side-by-side.
    """
    rbox(ax, x, y, w, h, CODE_BG, pad=3)
    n = max(len(lines_parts), 1)
    lh = (h - 8) / n
    for i, parts in enumerate(lines_parts):
        ly = y + h - 5 - i * lh - lh / 2
        render_inline(ax, x + 7, ly, parts, fs)


def search_blk(ax, x, y, w, h, call_parts, hdr, results, *, fs: float = 6.5):
    """A function-call block followed by a results header and result lines.

    Layout:
      line 1     →  syntax-highlighted call (e.g. ``recall.search("x")``)
      line 2     →  dim ``hdr`` (e.g. ``"Showing 3 of 3 results (page 1/1):"``)
      line 3+    →  ``results`` text
    """
    rbox(ax, x, y, w, h, CODE_BG, pad=3)
    n = 1 + 1 + len(results)
    lh = (h - 8) / n
    ly = y + h - 5 - lh / 2
    render_inline(ax, x + 7, ly, call_parts, fs)
    ly -= lh
    ax.text(x + 10, ly, hdr, va='center', color=LGRAY,
            fontsize=fs - 0.5, fontfamily='monospace', zorder=3)
    for r in results:
        ly -= lh
        ax.text(x + 13, ly, r, va='center', color=RES_TXT,
                fontsize=fs - 0.8, fontfamily='monospace', zorder=3)


# ─────────────────────────────────────────────────────────────────────────────
# Architecture-diagram primitives
# ─────────────────────────────────────────────────────────────────────────────
def diagram_box(ax, x, y, w, h, label, *,
                fc: str = '#d0d0d0', tc: str = '#111111', fw: str = 'normal',
                fs: float = 12, dashed: bool = False):
    """Rounded component box. Use ``dashed=True`` for an outlined / pending box."""
    ls = (0, (4, 2)) if dashed else 'solid'
    lw = 1.5 if dashed else 0
    ec = '#777' if dashed else 'none'
    ax.add_patch(FancyBboxPatch(
        (x + 4, y + 4), w - 8, h - 8,
        boxstyle="round,pad=4", fc=fc, ec=ec, lw=lw, ls=ls, zorder=2))
    ax.text(x + w / 2, y + h / 2, label, ha='center', va='center',
            color=tc, fontsize=fs, fontweight=fw, linespacing=1.3, zorder=3)


def diagram_drum(ax, x, y, w, h, label, *,
                 fc: str = '#4080c0', tc: str = '#ffffff',
                 fw: str = 'bold', fs: float = 12):
    """Storage 'drum' (cylinder) — flat body + ellipse cap on top."""
    bh = h * 0.78
    ax.add_patch(FancyBboxPatch((x + 4, y + 4), w - 8, bh - 4,
        boxstyle="round,pad=4", fc=fc, ec='none', zorder=2))
    ax.add_patch(mpatches.Ellipse(
        (x + w / 2, y + bh), w * 0.90, h * 0.26, fc=fc, ec='none', zorder=3))
    ax.text(x + w / 2, y + bh * 0.44, label, ha='center', va='center',
            color=tc, fontsize=fs, fontweight=fw, linespacing=1.3, zorder=4)


def uarrow(ax, x, y_bot, y_top, color, *, lw: float = 2.8, mut: float = 16):
    """Vertical arrow pointing UP (y_bot → y_top)."""
    ax.annotate('', xy=(x, y_top), xytext=(x, y_bot),
        arrowprops=dict(arrowstyle='->', color=color, lw=lw, mutation_scale=mut))


def harrow(ax, x0, x1, y, color, *, lw: float = 1.8, mut: float = 13):
    """Horizontal arrow (x0 → x1)."""
    ax.annotate('', xy=(x1, y), xytext=(x0, y),
        arrowprops=dict(arrowstyle='->', color=color, lw=lw, mutation_scale=mut))


def arc_arrow(ax, x0, y0, x1, y1, color, *,
              rad: float = -0.4, lw: float = 2.5, mut: float = 14):
    """Curved arrow from (x0, y0) → (x1, y1). Negative ``rad`` curves below."""
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                        connectionstyle=f'arc3,rad={rad}', mutation_scale=mut))


def context_brace(ax, x0, x1, y, label, *, tick: float = 8, fs: float = 13):
    """Top brace (horizontal line + downward ticks at the ends) with a centered
    label above. Mimics the LaTeX ``\\overbrace`` look used in many systems
    papers (e.g. MemGPT's "LLM Finite Context Window")."""
    ax.plot([x0, x1], [y, y], color='black', lw=1.2)
    for bx in (x0, x1):
        ax.plot([bx, bx], [y, y - tick], color='black', lw=1.2)
    ax.text((x0 + x1) / 2, y + 5, label,
            ha='center', va='bottom', fontsize=fs)
