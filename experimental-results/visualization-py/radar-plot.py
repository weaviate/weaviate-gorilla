import matplotlib.pyplot as plt
import numpy as np

# Data for the radar chart
categories = [
    "search",
    "integer filters",
    "text filters",
    "boolean filters",
    "integer aggregations",
    "text aggregations",
    "boolean aggregations",
    "groupby"
]

gpt_4o = [0.682, 0.725, 0.767, 0.816, 0.736, 0.742, 0.779, 0.665]
gpt_4o_mini = [0.55, 0.618, 0.602, 0.673, 0.686, 0.662, 0.695, 0.584]

# Add the first value at the end to close the radar chart loop
categories += [categories[0]]
gpt_4o += [gpt_4o[0]]
gpt_4o_mini += [gpt_4o_mini[0]]

# Angles for each axis
angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=True)

# Plotting
# Stylized Radar Chart with Semi-Transparent Outer Circle
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# Styling for gpt-4o
ax.plot(angles, gpt_4o, label="gpt-4o", color=cmap(2), linewidth=3)
ax.fill(angles, gpt_4o, color=cmap(2), alpha=0.3)

# Styling for gpt-4o-mini
ax.plot(angles, gpt_4o_mini, label="gpt-4o-mini", color=cmap(1), linewidth=3, linestyle='dashed')
ax.fill(angles, gpt_4o_mini, color=cmap(1), alpha=0.3)

# Enhance axis aesthetics
ax.set_yticks([0.2, 0.4, 0.6, 0.8])
ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8"], color="gray", fontsize=12)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories[:-1], color="darkgreen", fontsize=14)

# Customize outer circle with transparency
ax.spines['polar'].set_edgecolor("black")
ax.spines['polar'].set_alpha(0.5)  # Add transparency to the border

# Add a legend and title
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12, frameon=False)
ax.set_title("gpt-4o vs. gpt-4o-mini", color="darkgreen", fontsize=16, weight="bold")

# Set background color and grid styling
ax.set_facecolor("#f7fff7")
ax.grid(color="lightgray", linestyle="--", linewidth=0.5)

plt.show()

