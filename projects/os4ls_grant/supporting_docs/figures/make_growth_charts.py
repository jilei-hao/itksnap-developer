#!/usr/bin/env python3
"""Regenerate ITK-SNAP growth charts (panels d,e of the Overview figure).
Data (2013-2025), pulled 2026-07-15:
  Downloads: SourceForge public stats API (project itk-snap).
  Citations: OpenAlex counts_by_year for the ITK-SNAP methods paper
             (Yushkevich 2006, doi:10.1016/j.neuroimage.2006.01.015).
"""
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = "/private/tmp/claude-501/-Users-jileihao-dev-itksnap-dev-itksnap-developer/fc47a0d6-3893-406a-8a95-ce4e666af31f/scratchpad"

years = list(range(2013, 2026))
downloads = [23714, 32828, 35836, 42736, 39567, 47164, 65325,
             83014, 90766, 110004, 118532, 155961, 167444]
citations = [201, 239, 344, 350, 452, 493, 598,
             766, 968, 911, 896, 956, 873]

BAR   = "#4E79A7"   # steel blue (matches the R01 look)
INK   = "#222222"
GRID  = "#D9D9D9"
MUTE  = "#6B6B6B"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 12,
    "axes.edgecolor": "#BFBFBF",
    "axes.linewidth": 0.8,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})

fig, (axd, axc) = plt.subplots(1, 2, figsize=(9.6, 2.9), dpi=300)

def style(ax, title, subtitle):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=GRID, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14, loc="left")
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=10.5, color=MUTE)
    ax.set_xticks(years[::2])
    ax.set_xticklabels([str(y) for y in years[::2]])
    ax.tick_params(length=0)
    ax.margins(x=0.02)

# (d) Downloads
axd.bar(years, downloads, color=BAR, width=0.72, zorder=3)
axd.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v/1000)}K" if v else "0"))
style(axd, "(d) Annual downloads, 2013–2025", "SourceForge  ·  >1.0M total in range, >1.1M lifetime")

# (e) Citations
axc.bar(years, citations, color=BAR, width=0.72, zorder=3)
style(axc, "(e) Annual citations, 2013–2025", "Methods paper (OpenAlex)  ·  ~8.0K in range")

fig.tight_layout(w_pad=3.0)
fig.savefig(f"{OUT}/itksnap_growth_charts.png", dpi=300, bbox_inches="tight",
            facecolor="white", pad_inches=0.12)
print("saved", f"{OUT}/itksnap_growth_charts.png")
print("downloads 2013-2025 total:", sum(downloads))
print("citations 2013-2025 total:", sum(citations))
