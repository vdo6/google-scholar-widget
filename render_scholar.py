
#!/usr/bin/env python3
"""Generate Google Scholar PNG from saved statistics."""

import json
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent

DATA = ROOT / "scholar_data.json"
OUTPUT = ROOT / "scholar.png"

SCHOLAR_ID = "Xa97hl4AAAAJ"

# Read real statistics
with DATA.open(encoding="utf-8") as f:
    data = json.load(f)

if data.get("scholar_id") != SCHOLAR_ID:
    raise ValueError("Incorrect Google Scholar profile")

citations = int(data["citations"])
hindex = int(data["hindex"])
i10index = int(data["i10index"])
updated = str(data["updated"])

yearly = data["cites_per_year"]

if not yearly:
    raise ValueError("Missing annual citations")

years = sorted(int(y) for y in yearly)
values = [int(yearly[str(y)]) for y in years]

# Colors
BG = "#202020"
RED = "#cc0000"
WHITE = "#ffffff"
GRAY = "#bbbbbb"
GRID = "#555555"

# Figure
fig = plt.figure(
    figsize=(13, 7),
    facecolor=BG
)

# Main title
fig.text(
    0.055, 0.94,
    "Google Scholar",
    color=WHITE,
    fontsize=26,
    fontweight="light"
)

# Metrics
metrics = [
    ("Citations", f"{citations:,}"),
    ("h-index", str(hindex)),
    ("i10-index", str(i10index))
]

for x, (label, value) in zip(
    [0.055, 0.26, 0.45], metrics
):
    fig.text(
        x, 0.855, label,
        color=GRAY, fontsize=13
    )
    fig.text(
        x, 0.795, value,
        color=WHITE, fontsize=25
    )

# Source information
fig.text(
    0.055, 0.72,
    f"According to Google Scholar  |  Updated {updated}",
    color=GRAY,
    fontsize=11
)

# Chart area
ax = fig.add_axes([0.075, 0.16, 0.88, 0.48])
ax.set_facecolor(BG)

x = np.arange(len(years))

bars = ax.bar(
    x,
    values,
    width=0.68,
    color=RED
)

# Chart labels
max_value = max(values)
upper = max_value * 1.20 if max_value else 1

ax.set_ylim(0, upper)

for bar, value in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + upper * 0.015,
        str(value),
        ha="center",
        va="bottom",
        fontsize=9,
        color=WHITE
    )

ax.set_xticks(x)
ax.set_xticklabels(
    years,
    fontsize=10,
    color=WHITE
)

ax.tick_params(
    axis="y",
    colors=WHITE,
    labelsize=10,
    length=0
)
ax.tick_params(
    axis="x",
    length=0,
    pad=12
)

ax.yaxis.grid(
    True,
    color=GRID,
    alpha=0.65,
    linewidth=0.8
)

ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Profile and footer
fig.text(
    0.055, 0.055,
    "scholar.google.com/citations?user=Xa97hl4AAAAJ",
    color=GRAY,
    fontsize=10
)

fig.savefig(
    OUTPUT,
    dpi=150,
    facecolor=BG,
    bbox_inches="tight",
    pad_inches=0.25
)

plt.close(fig)

print(f"Image generated: {OUTPUT}")
