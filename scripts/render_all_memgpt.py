#!/usr/bin/env python3
"""
Reference example for the paper-to-image skill.

Generates all 8 figures from the MemGPT paper (arXiv 2310.08560) at the
exact pixel dimensions of the benchmark images in ``output/benchmark/``.

Usage (from project root):
    python3 scripts/render_all_memgpt.py

Output → ``output/generated/<timestamp>-figure*.png``

This file is the worked example that the SKILL.md references. To produce
figures for a different paper, copy ``scripts/render_paper_template.py``
and rewrite each ``gen_figureN()`` for that paper's figure catalog.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

from render_helpers import (
    DPI,
    BG, AI_BUB, AI_TC, USR_BUB, USR_TC, CODE_BG,
    RED_FG, GRN_FG, GRAY, LGRAY, RES_TXT,
    CALL_TEL, FN_YEL, STR_GRN, OLD_RED, NEW_GRN,
    new_canvas, timestamp, save_pixel,
    rbox, bubble, alert_line, code_blk, search_blk,
    diagram_box, diagram_drum, uarrow, harrow, arc_arrow, context_brace,
)

TS = timestamp()


def save(fig, slug):
    path = f'output/generated/{TS}-{slug}.png'
    save_pixel(fig, path)
    print(f'  ✓  {path}')


# ── Figure 1 — Birthday chat, memory pressure (295×171) ─────────────────────
def gen_figure1():
    W, H = 295, 171
    fig, ax = new_canvas(W, H)
    ax.text(W/2, 163, 'February 7', ha='center', va='center',
            color=GRAY, fontsize=7.5, zorder=3)
    bubble(ax, 5,  130, 188, 26, AI_BUB,  'How was your day today?',
           fs=7.5, tc=AI_TC)
    bubble(ax, 85, 98,  205, 26, USR_BUB,
           'fun my bf james baked me\na birthday cake', ha='center', fs=7)
    bubble(ax, 5,  66,  188, 26, AI_BUB,  'Oh wow, happy birthday!',
           fs=7.5, tc=AI_TC)
    alert_line(ax, 54, 'System Alert: Memory Pressure', RED_FG, fs=7)
    code_blk(ax, 5, 32, W-10, 18,
             [[('working_context.append(', FN_YEL),
               ('"Birthday is February 7")', STR_GRN)]], fs=6.5)
    code_blk(ax, 5, 10, W-10, 18,
             [[('working_context.append(', FN_YEL),
               ('"Boyfriend named James")',  STR_GRN)]], fs=6.5)
    save(fig, 'figure')


# ── Figure 2 — Recall search "six flags" (315×175) ──────────────────────────
def gen_figure2():
    W, H = 315, 175
    fig, ax = new_canvas(W, H)
    ax.text(W/2, 168, 'February 7', ha='center', va='center',
            color=GRAY, fontsize=7.5, zorder=3)
    bubble(ax, 5, 133, 210, 28, AI_BUB,
           'Did you do anything else to celebrate\nyour birthday?',
           fs=7.5, tc=AI_TC)
    bubble(ax, 90, 99, 220, 28, USR_BUB,
           'yeah we went to six flags!', ha='center', fs=7.5)
    search_blk(ax, 5, 28, W-10, 66,
               call_parts=[('recall_storage.search(', CALL_TEL),
                            ('"six flags"',            FN_YEL),
                            (')',                      CALL_TEL)],
               hdr='Showing 3 of 3 results (page 1/1):',
               results=[
                   '[01/24/2024] "lol yeah six flags"',
                   '[01/14/2024] "i love six flags been like 100 times"',
                   '[10/12/2023] "james and I actually first met at six flags"',
               ], fs=6.5)
    bubble(ax, 5, 6, 220, 20, AI_BUB,
           "Did you go with James? It's so cute how both met there!",
           fs=7, tc=AI_TC)
    save(fig, 'figure_2')


# ── Figure 3 — Architecture diagram (1088×430) ───────────────────────────────
def gen_figure3():
    PX_W, PX_H = 1088, 430
    fig = plt.figure(figsize=(PX_W / DPI, PX_H / DPI))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PX_W);  ax.set_ylim(0, PX_H)
    ax.axis('off')

    # Component palette (face_color, text_color, font_weight)
    SYS   = ('#111111', 'white',   'bold')
    WCTX  = ('#f08c00', '#111111', 'bold')
    FIFO  = ('#c050c0', 'white',   'bold')
    OBUF  = ('white',   '#111111', 'bold')
    ARCH  = ('#40a040', 'white',   'bold')
    REC   = ('#4080c0', 'white',   'bold')
    NEUT  = ('#d0d0d0', '#111111', 'normal')

    # ── title brace ──────────────────────────────────────────────────────────
    context_brace(ax, 28, 675, 395,
                  'LLM Finite Context Window (e.g. 8k tokens)', fs=13)

    # ── section labels ───────────────────────────────────────────────────────
    ax.text(280, 381, 'Prompt Tokens',
            ha='center', va='top', fontsize=9, color='#444')
    ax.text(640, 381, 'Completion Tokens',
            ha='center', va='top', fontsize=9, color='#444')

    # ── dashed bounding box around the 3 prompt-tokens components ────────────
    ax.add_patch(plt.Rectangle((25, 262), 518, 126,
        fill=False, ec='black', lw=1.3, ls='--', zorder=1))

    # ── top row boxes (prompt tokens + output buffer) ────────────────────────
    diagram_box(ax,  28, 265, 190, 120, 'System\nInstructions',
                fc=SYS[0],  tc=SYS[1],  fw=SYS[2],  fs=13)
    diagram_box(ax, 228, 265, 210, 120, 'Working\nContext',
                fc=WCTX[0], tc=WCTX[1], fw=WCTX[2], fs=13)
    diagram_box(ax, 448, 265,  90, 120, 'FIFO\nQueue',
                fc=FIFO[0], tc=FIFO[1], fw=FIFO[2], fs=11)
    diagram_box(ax, 548, 265, 125, 120, 'Output\nBuffer',
                fc=OBUF[0], tc=OBUF[1], fw=OBUF[2], fs=12, dashed=True)

    lfs = 7.5
    ax.text(123, 256, 'Read-Only (static)\nMemGPT System Prompt',
            ha='center', va='top', fontsize=lfs, color='#555', linespacing=1.3)
    ax.text(333, 256, 'Read-Write\nWrite via Functions',
            ha='center', va='top', fontsize=lfs, color='#555', linespacing=1.3)
    ax.text(493, 256, 'Read-Write\nWrite via Queue Manager',
            ha='center', va='top', fontsize=lfs, color='#555', linespacing=1.3)

    # ── bottom row: external storage + executors ─────────────────────────────
    diagram_drum(ax,  28,  55, 175, 140, 'Archival\nStorage',
                 fc=ARCH[0], tc=ARCH[1], fw=ARCH[2], fs=13)
    diagram_box (ax, 220,  70, 185, 115, 'Function\nExecutor',
                 fc=NEUT[0], tc=NEUT[1], fw=NEUT[2], fs=12)
    diagram_box (ax, 430,  70, 185, 115, 'Queue\nManager',
                 fc=NEUT[0], tc=NEUT[1], fw=NEUT[2], fs=12)
    diagram_drum(ax, 640,  55, 175, 140, 'Recall\nStorage',
                 fc=REC[0],  tc=REC[1],  fw=REC[2],  fs=13)

    ax.text(115, 48, 'Read via Functions\nWrite via Functions',
            ha='center', va='top', fontsize=lfs, color='#555', linespacing=1.3)
    ax.text(727, 48, 'Read via Functions\nWrite via Queue Manager',
            ha='center', va='top', fontsize=lfs, color='#555', linespacing=1.3)

    # ── vertical arrows (bottom row → top row) ───────────────────────────────
    uarrow(ax, 333, 185, 265, '#f08c00', lw=3.2)   # Func Exec → Working Context
    uarrow(ax, 475, 185, 265, '#c050c0', lw=3.2)   # Q Mgr → FIFO Queue (pink)
    uarrow(ax, 510, 185, 265, '#4080c0', lw=3.2)   # Q Mgr → FIFO Queue (blue)

    # ── horizontal arrows (bottom row) ───────────────────────────────────────
    harrow(ax, 203, 220, 148, '#40a040')   # Archival ↔ Func Exec (green)
    harrow(ax, 220, 203, 128, '#40a040')
    harrow(ax, 405, 430, 143, '#333')      # Func Exec ↔ Q Mgr (black)
    harrow(ax, 430, 405, 123, '#333')
    harrow(ax, 615, 640, 143, '#4080c0')   # Q Mgr → Recall Storage (blue, one-way)

    # ── large blue arc: Recall Storage → Function Executor ───────────────────
    arc_arrow(ax, 640, 112, 405, 112, '#4080c0', rad=-0.45, lw=2.5)

    save_pixel(fig, f'output/generated/{TS}-figure_3.png', bg='white')
    print(f'  ✓  output/generated/{TS}-figure_3.png')


# ── Figure 4 — Feb-14 breakup, working_context.replace (334×194) ─────────────
def gen_figure4():
    W, H = 334, 194
    fig, ax = new_canvas(W, H)
    ax.text(W/2, 185, 'February 14', ha='center', va='center',
            color=GRAY, fontsize=7.5, zorder=3)
    bubble(ax, 5, 148, 210, 30, AI_BUB,
           "How's James doing? Any special plans today?",
           fs=7.5, tc=AI_TC)
    bubble(ax, 115, 110, 214, 30, USR_BUB,
           'actually james and i broke up', ha='center', fs=7.5)
    code_blk(ax, 5, 22, W-10, 84,
             [
                 [('working_context.replace(', FN_YEL)],
                 [('  ', RES_TXT), ('"Boyfriend named James",',   OLD_RED)],
                 [('  ', RES_TXT), ('"Ex-boyfriend named James"', NEW_GRN)],
                 [(')', RES_TXT)],
             ], fs=7.0)
    bubble(ax, 5, 2, 200, 18, AI_BUB,
           "Sorry to hear that - hope you're OK", fs=7.5, tc=AI_TC)
    save(fig, 'figure_4')


# ── Figure 5 — Document QA accuracy vs docs retrieved (322×217) ──────────────
# Data follows the paper's narrative: fixed-context models RISE then FALL as
# documents fill the 8k context window; MemGPT lines stay flat (unbounded).
def gen_figure5():
    X = [0, 25, 50, 75, 100, 125, 150, 175, 200]
    SERIES = [
        ('GPT-4',
         [0.40, 0.60, 0.70, 0.60, 0.38, 0.28, 0.20, 0.14, 0.10],
         '#1f77b4', '--', 's', 4),
        ('GPT-3.5 Turbo',
         [0.38, 0.42, 0.48, 0.42, 0.30, 0.20, 0.13, 0.10, 0.08],
         '#aec7e8', '-.', 'D', 4),
        ('GPT-4 Turbo',
         [0.62, 0.62, 0.62, 0.62, 0.62, 0.62, 0.62, 0.62, 0.60],
         '#17becf', ':', '^', 4),
        ('MemGPT (GPT-4, GPT-4 Turbo)',
         [0.65, 0.67, 0.68, 0.67, 0.68, 0.68, 0.67, 0.66, 0.60],
         '#2ca02c', '-', 's', 4),
        ('MemGPT (GPT-3.5)',
         [0.40, 0.45, 0.50, 0.44, 0.38, 0.30, 0.22, 0.16, 0.10],
         '#d62728', '--', 'v', 4),
    ]
    fig, ax = plt.subplots(figsize=(3.22, 2.17))
    fig.patch.set_facecolor('white');  ax.set_facecolor('white')
    for label, ys, color, ls, marker, ms in SERIES:
        ax.plot(X, ys, color=color, linestyle=ls, marker=marker,
                markersize=ms, linewidth=1.1, label=label)
    ax.axhline(0.40, color='#c44433', linestyle='--', linewidth=0.9, zorder=1)
    ax.set_xlabel('Documents Retrieved', fontsize=7.5)
    ax.set_ylabel('Accuracy',            fontsize=7.5)
    ax.set_ylim(0.05, 0.75);  ax.set_xlim(-5, 210)
    ax.grid(True, linestyle='-', linewidth=0.25, color='#e0e0e0', zorder=0)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=5.2, loc='lower left', framealpha=0.95,
              handlelength=2.0, handletextpad=0.4, borderpad=0.4,
              ncol=1, columnspacing=0.6, labelspacing=0.3)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5);  spine.set_color('#bbbbbb')
    plt.tight_layout(pad=0.25)
    plt.savefig(f'output/generated/{TS}-figure_5.png', dpi=DPI, facecolor='white')
    plt.close(fig)
    print(f'  ✓  output/generated/{TS}-figure_5.png')


# ── Figure 6 — Nobel Prize archival search (335×250) ─────────────────────────
def gen_figure6():
    W, H = 335, 250
    fig, ax = new_canvas(W, H)
    alert_line(ax, 242, 'System Alert: Archive Storage Upload Complete',
               GRN_FG, fs=7)
    bubble(ax, 85, 200, 245, 36, USR_BUB,
           'Who won the first Nobel Prize in physics?', ha='center', fs=7.5)
    search_blk(ax, 5, 118, W-10, 78,
               call_parts=[('archival_storage.search(', CALL_TEL),
                            ('"nobel physics"',          FN_YEL),
                            (')',                        CALL_TEL)],
               hdr='Showing 10 of 124 results (page 1/13):',
               results=[
                   '"The Nobel Prizes, beginning in 1901, and the ...',
                   '"This award is administered by the Nobel Foundation...',
                   '...',
               ], fs=6.3)
    search_blk(ax, 5, 32, W-10, 82,
               call_parts=[('archival_storage.search(', CALL_TEL),
                            ('"nobel physics"',          FN_YEL),
                            (', page=2)',                CALL_TEL)],
               hdr='Showing 10 of 124 results (page 2/13):',
               results=[
                   '"The Nobel Prize in Physics is a yearly award given...',
                   '"The 1901 Nobel in physics was awarded to Wilhelm ...',
                   '...',
               ], fs=6.3)
    bubble(ax, 5, 8, 175, 22, AI_BUB, 'Wilhelm Conrad Rontgen',
           fs=7.5, tc=AI_TC)
    save(fig, 'figure_6')


# ── Figure 7 — Nested KV accuracy vs nesting level (317×208) ─────────────────
def gen_figure7():
    X = [0, 1, 2, 3]
    SERIES = [
        ('GPT-3.5',              [0.40, 0.02, 0.0,  0.0],  '#1f77b4', '--',  's', 4),
        ('GPT-4 Turbo',          [0.87, 0.27, 0.05, 0.0],  '#ff7f0e', '-.',  '^', 4),
        ('GPT-4',                [0.83, 0.23, 0.04, 0.0],  '#aec7e8', ':',   'D', 4),
        ('MemGPT (GPT-4 Turbo)', [1.0,  1.0,  0.67, 0.60], '#d62728', '-',   'o', 5),
        ('MemGPT (GPT-3.5)',     [0.60, 0.27, 0.03, 0.0],  '#ff7f0e', '--',  'v', 4),
        ('MemGPT (GPT-4)',       [0.87, 0.50, 0.17, 0.03], '#1f77b4', '--',  's', 4),
    ]
    fig, ax = plt.subplots(figsize=(3.17, 2.08))
    fig.patch.set_facecolor('white');  ax.set_facecolor('white')
    for label, ys, color, ls, marker, ms in SERIES:
        ax.plot(X, ys, color=color, linestyle=ls, marker=marker,
                markersize=ms, linewidth=1.1, label=label)
    ax.set_xlabel('Nesting Level', fontsize=7.5)
    ax.set_ylabel('Accuracy',      fontsize=7.5)
    ax.set_ylim(-0.02, 1.06);  ax.set_xlim(-0.15, 3.15)
    ax.set_xticks([0, 1, 2, 3])
    ax.grid(True, linestyle='-', linewidth=0.25, color='#e0e0e0', zorder=0)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=5.0, loc='upper right', framealpha=0.95,
              handlelength=2.0, handletextpad=0.4, borderpad=0.4,
              ncol=2, columnspacing=0.6, labelspacing=0.3)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5);  spine.set_color('#bbbbbb')
    plt.tight_layout(pad=0.25)
    plt.savefig(f'output/generated/{TS}-figure_7.png', dpi=DPI, facecolor='white')
    plt.close(fig)
    print(f'  ✓  output/generated/{TS}-figure_7.png')


# ── Figure 8 — Nested KV key-value search (340×306) ─────────────────────────
def gen_figure8():
    W, H = 340, 306
    fig, ax = new_canvas(W, H)
    alert_line(ax, 298, 'System Alert: Archive Storage Upload Complete',
               GRN_FG, fs=7)
    bubble(ax, 90, 256, 245, 36, USR_BUB,
           'Find the value for key 831\u2026ea5', ha='center', fs=7.5)
    search_blk(ax, 5, 186, W-10, 66,
               call_parts=[('archival_storage.search(', CALL_TEL),
                            ('"831...ea5"',              FN_YEL),
                            (')',                        CALL_TEL)],
               hdr='Showing 1 of 1 results (page 1/1):',
               results=['"Key: 831\u2026ea5, Value: 5b8\u20144c3"'],
               fs=6.3)
    search_blk(ax, 5, 104, W-10, 78,
               call_parts=[('archival_storage.search(', CALL_TEL),
                            ('"5b8...4c3"',              FN_YEL),
                            (')',                        CALL_TEL)],
               hdr='Showing 2 of 2 results (page 1/1):',
               results=[
                   '"Key: 5b8\u20144c3, Value: f37\u2014617"',
                   '"Key: 831\u2026ea5, Value: 5b8\u20144c3"',
               ], fs=6.3)
    search_blk(ax, 5, 30, W-10, 70,
               call_parts=[('archival_storage.search(', CALL_TEL),
                            ('"f37...617"',              FN_YEL),
                            (')',                        CALL_TEL)],
               hdr='Showing 1 of 1 results (page 1/1):',
               results=['"Key: 5b8\u20144c3, Value: f37\u2014617"'],
               fs=6.3)
    bubble(ax, 5, 6, 110, 22, AI_BUB, 'f37\u2026617', fs=7.5, tc=AI_TC)
    save(fig, 'figure_8')


# ── Run all ──────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(f'Generating MemGPT reference figures → output/generated/  [{TS}]')
    gen_figure1()
    gen_figure2()
    gen_figure3()
    gen_figure4()
    gen_figure5()
    gen_figure6()
    gen_figure7()
    gen_figure8()
    print('Done — 8 figures saved.')
