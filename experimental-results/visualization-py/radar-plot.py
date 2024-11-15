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
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

ax.plot(angles, gpt_4o, label="gpt-4o", linewidth=2)
ax.fill(angles, gpt_4o, alpha=0.25)

ax.plot(angles, gpt_4o_mini, label="gpt-4o-mini", linewidth=2, linestyle='dashed')
ax.fill(angles, gpt_4o_mini, alpha=0.25)

# Add category labels
ax.set_yticks([0.2, 0.4, 0.6, 0.8])
ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8"])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories[:-1])

# Add legend and title
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax.set_title("Radar Chart: Comparison of gpt-4o and gpt-4o-mini", va='bottom')

plt.show()
