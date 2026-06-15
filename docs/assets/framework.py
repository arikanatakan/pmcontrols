"""Generate the pmcontrols framework figure (academic style).

Two stages: the validated core, and the optional visualization layer.
Run:  python docs/assets/framework.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5})

INK = "#1f2d3d"
MUT = "#5b6b7b"
CORE_F, CORE_E = "#eef3f8", "#3b6ea5"
RES_F, RES_E = "#d4e4f4", "#2c5f8a"
BAN_F, BAN_E = "#f5f7f9", "#cdd6df"
OPT_BG, OPT_E = "#f2faf7", "#3a8f78"
OPT_F = "#e3f1ec"
ARROW = "#7c8a99"

fig, ax = plt.subplots(figsize=(11.5, 7.6))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box(x, y, w, h, text, fill=CORE_F, edge=CORE_E, dashed=False, fs=8.4,
        bold=False, tcol=INK):
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.35,rounding_size=1.4",
        linewidth=1.25, edgecolor=edge, facecolor=fill,
        linestyle="--" if dashed else "-", zorder=2))
    ax.text(x, y, text, ha="center", va="center", color=tcol, fontsize=fs,
            fontweight="bold" if bold else "normal", zorder=5)


def arrow(x0, y0, x1, y1, color=ARROW, dashed=False, lw=1.15):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=1,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                linestyle="--" if dashed else "-",
                                shrinkA=1, shrinkB=1))


# ---- Stage 1: validated core ------------------------------------------------
ax.text(3, 97.5, "1   Validated core", fontsize=13.5, fontweight="bold",
        color=INK, ha="left")
for x, t in [(14, "Inputs"), (38, "Analyses"), (64, "Result"),
             (88, "Consumption")]:
    ax.text(x, 92.5, t, ha="center", fontsize=9.5, color=MUT, fontstyle="italic")

inputs = ["activities\n(id, predecessors, duration)", "three-point estimate\n(a, m, b)",
          "crash data\n(+ crash cost per period)", "PMB\n(periods, planned value)"]
analyses = ["cpm()\ncritical path", "pert()\nMonte Carlo schedule risk",
            "crash()\ntime / cost trade-off LP",
            "plan() / evm()\nearned_schedule()"]
rows = [87, 78, 69, 60]
for t, y in zip(inputs, rows):
    box(14, y, 21, 6.6, t, fs=7.9)
for t, y in zip(analyses, rows):
    box(38, y, 22, 6.6, t, fs=7.9)

box(64, 73.5, 21, 28, "Result\n\nstats  ·  table  ·  alerts\n\nmeta\nversion · input hash\ntimestamp",
    fill=RES_F, edge=RES_E, fs=9, bold=True)

consume = ["r.ok\npass / fail gate", "summary()\nplain-text verdict",
           "to_dict()\nJSON, versioned"]
crows = [85, 73.5, 62]
for t, y in zip(consume, crows):
    box(88, y, 19, 7.4, t, fs=7.9)

for y in rows:
    arrow(24.7, y, 26.8, y)
for y in rows:
    arrow(49.2, y, 53.3, 73.5)
for y in crows:
    arrow(74.6, 73.5, 78.4, y)

box(50, 51.5, 94, 5.6,
    "computed from the defining formulations    ·    validated against published "
    "reference values on every CI run    ·    headless (CI, cron, agents)",
    fill=BAN_F, edge=BAN_E, fs=8.2, tcol=MUT)

# ---- Stage 2: optional visualization layer ----------------------------------
ax.add_patch(FancyBboxPatch((4, 5.5), 92, 33,
             boxstyle="round,pad=0.4,rounding_size=1.6",
             linewidth=1.4, edgecolor=OPT_E, facecolor=OPT_BG,
             linestyle="--", zorder=0))
ax.text(7, 34.2, "2   Optional visualization layer", fontsize=13.5,
        fontweight="bold", color="#2e7d6b", ha="left")
ax.text(7, 30.3, "pip install pmcontrols[plot]    ·    matplotlib, kept separate "
        "from the validated statistics", fontsize=8.2, color=OPT_E,
        ha="left", fontstyle="italic")

box(13, 21, 15, 8, "Result", fill=RES_F, edge=RES_E, fs=9, bold=True)
arrow(64, 59.5, 13, 25.2, color=OPT_E, dashed=True, lw=1.3)

charts = ["gantt()", "network_diagram()", "evm_curve()", "criticality()",
          "mc_distribution()"]
cx = [33, 46.5, 60, 73.5, 87]
for t, x in zip(charts, cx):
    box(x, 21, 12.8, 8, t, fill=OPT_F, edge=OPT_E, fs=7.8)
for x in cx:
    arrow(20.6, 21, x - 6.7, 21, color=OPT_E)
box(60, 10.5, 44, 5, "matplotlib figures   (PNG / SVG / PDF)",
    fill="#e3f1ec", edge=OPT_E, fs=8.2, tcol="#2e7d6b")
for x in cx:
    arrow(x, 16.8, 60, 13.2, color=OPT_E)

fig.savefig("docs/assets/framework.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("wrote docs/assets/framework.png")
