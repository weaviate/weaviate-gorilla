import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import umap
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys
from openai import OpenAI

# Set random seed for reproducibility
np.random.seed(42)

# Initialize OpenAI client as a global variable
openai_client = OpenAI(api_key="")

# Sample texts - you can expand this list with your own texts
texts = [
    "Compare the average length of active and inactive machine learning fundamentals courses.",
    "What's the mean duration of machine learning fundamentals courses, separated by enrollment status?",
    "Show me how average course duration differs between open and closed machine learning fundamentals courses.",
    "Calculate the typical time commitment for machine learning fundamentals courses based on whether they're currently accepting students.",
    "For courses teaching machine learning fundamentals, what's the average duration when grouped by enrollment availability?",
    "How long do machine learning fundamentals courses typically run? Break it down by current enrollment status.",
    "Is there a difference in average course length between ongoing and upcoming machine learning fundamentals courses?",
    "What is the mean time length of machine learning fundamentals courses that are enrolling compared to those that aren't?",
    "Compare average course duration for active versus inactive machine learning fundamentals offerings.",
    "Find the typical course length for machine learning fundamentals programs, divided by enrollment status.",
    "I want to see the average duration of machine learning fundamentals courses, separated by whether they're currently enrolling or not.",
    "What's the mean time commitment for machine learning fundamentals courses that are open for enrollment versus closed ones?",
    "Analyze the average length of machine learning fundamentals courses by their current enrollment status.",
    "How does course duration for machine learning fundamentals differ between courses currently accepting students and those that aren't?",
    "Calculate the average time span of available versus unavailable machine learning fundamentals courses.",
    "What's the typical duration of a machine learning fundamentals course? Show the difference between enrolling and non-enrolling courses.",
    "Compare average timeframes for machine learning fundamentals courses based on their enrollment availability.",
    "For \"machine learning fundamentals\" courses, show me the mean duration grouped by enrollment status.",
    "What duration can I expect for machine learning fundamentals courses that are currently enrolling versus those that aren't?",
    "Find the average length of machine learning fundamentals courses and compare enrolling versus non-enrolling options.",
    "Calculate mean course duration for machine learning fundamentals, segmented by current enrollment status.",
    "How long are machine learning fundamentals courses on average? Differentiate between those currently accepting students and those that aren't.",
    "Compare the typical time investment for open versus closed machine learning fundamentals courses.",
    "What's the average duration difference between enrolling and non-enrolling machine learning fundamentals courses?",
    "For courses about machine learning fundamentals, show me average durations grouped by enrollment availability.",
    "How do course lengths compare between active and inactive machine learning fundamentals courses?",
    "Calculate the mean duration of machine learning fundamentals courses where enrollment is open versus courses where it's closed.",
    "What's the typical time commitment for a machine learning fundamentals course? Show data for both enrolling and non-enrolling options.",
    "I need the average time span of machine learning fundamentals courses, categorized by enrollment status.",
    "Show me how long machine learning fundamentals courses typically run, separating those currently enrolling from those that aren't.",
    "What's the mean course length for machine learning fundamentals, distinguished by enrollment availability?",
    "Find average course durations for machine learning fundamentals, broken down by whether they're accepting new students.",
    "Compare the average time to complete machine learning fundamentals courses that are enrolling versus those that aren't.",
    "How long do machine learning fundamentals courses take on average? Differentiate by enrollment status.",
    "Calculate the typical duration of \"machine learning fundamentals\" courses and compare based on current enrollment availability.",
    "For machine learning fundamentals content, what's the average course length when separated by enrollment status?",
    "Is there a difference in time commitment between open and closed enrollment machine learning fundamentals courses?",
    "What can you tell me about the average duration of machine learning fundamentals courses based on their enrollment status?",
    "Compare the mean time length of machine learning fundamentals courses that are currently taking students versus those that aren't.",
    "How does the average duration of machine learning fundamentals courses vary with enrollment status?",
    "What's the expected time commitment for machine learning fundamentals courses? Show me the difference between current and future offerings.",
    "Give me the average length of time for machine learning fundamentals courses, divided between those enrolling and not enrolling.",
    "Calculate average durations for machine learning fundamentals courses and segment by enrollment availability.",
    "How do machine learning fundamentals courses compare in average duration when grouped by enrollment status?",
    "What's the mean time span of machine learning fundamentals courses that are accepting students versus those that aren't?",
    "Tell me the average duration of both active and inactive machine learning fundamentals courses.",
    "For courses focused on machine learning fundamentals, what's the typical length when separated by enrollment status?",
    "Compare time commitments between currently enrolling and not currently enrolling machine learning fundamentals courses.",
    "I'd like to know the average duration of machine learning fundamentals courses, with data separated by enrollment availability.",
    "What's the mean length of time required for machine learning fundamentals courses, contrasting those currently open with those closed for enrollment?"
]

def get_openai_embeddings(texts):
    """
    Get embeddings using OpenAI's API.
    
    Args:
        texts (list): List of text strings to embed
        
    Returns:
        numpy.ndarray: Array of embeddings
    """
    # Use the global OpenAI client
    global openai_client
    
    # Process texts in batches to avoid API limitations
    all_embeddings = []
    batch_size = 20  # Adjust based on API limits
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        # Get embeddings for the batch
        response = openai_client.embeddings.create(
            input=batch,
            model="text-embedding-3-small"  # You can also use "text-embedding-3-large" for higher quality
        )
        
        # Extract embeddings from response
        batch_embeddings = [data.embedding for data in response.data]
        all_embeddings.extend(batch_embeddings)
    
    # Convert to numpy array
    embeddings = np.array(all_embeddings)
    return embeddings

# Get embeddings using OpenAI API
print("Getting text embeddings from OpenAI API...")
embeddings = get_openai_embeddings(texts)
print(f"Embeddings shape: {embeddings.shape}")

# Calculate similarity matrix
print("\nCalculating similarity matrix...")
similarities = cosine_similarity(embeddings)
print("Similarity matrix:")
for i, text in enumerate(texts):
    print(f"Text {i+1}: {text}")
print(pd.DataFrame(similarities.round(2), index=[f"T{i+1}" for i in range(len(texts))],
                  columns=[f"T{i+1}" for i in range(len(texts))]))

# Reduce dimensions with UMAP
print("\nReducing dimensions with UMAP...")
umap_reducer = umap.UMAP(
    n_neighbors=5,
    min_dist=0.1,
    n_components=2,
    metric='cosine',
    random_state=42
)
umap_embeddings = umap_reducer.fit_transform(embeddings)
print(f"UMAP embeddings shape: {umap_embeddings.shape}")

# Cluster with HDBSCAN
print("\nClustering with HDBSCAN...")
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=2,
    min_samples=1,
    metric='euclidean',
    cluster_selection_epsilon=0.5,
    gen_min_span_tree=True
)
cluster_labels = clusterer.fit_predict(umap_embeddings)
num_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
print(f"Number of clusters found: {num_clusters}")

# Visualize the results
print("\nVisualizing the results...")
plt.figure(figsize=(12, 8))

# Create a color map with a special color for noise points (-1)
unique_labels = set(cluster_labels)
colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_labels) - (1 if -1 in unique_labels else 0)))
color_map = {}
color_index = 0

for label in unique_labels:
    if label == -1:
        color_map[label] = [0, 0, 0, 1]  # Black for noise points
    else:
        color_map[label] = colors[color_index]
        color_index += 1

# Plot points
for label in unique_labels:
    mask = cluster_labels == label
    
    if label == -1:
        # Noise points as black X
        plt.scatter(
            umap_embeddings[mask, 0],
            umap_embeddings[mask, 1],
            c=[color_map[label]],
            marker='x',
            s=100,
            linewidth=1,
            label=f"Noise"
        )
    else:
        # Regular clusters as circles with different colors
        plt.scatter(
            umap_embeddings[mask, 0],
            umap_embeddings[mask, 1],
            c=[color_map[label]],
            s=100,
            label=f"Cluster {label+1}"
        )

# Annotate points with text labels
for i, (x, y) in enumerate(umap_embeddings):
    plt.annotate(
        f"{i+1}",
        (x, y),
        fontsize=9,
        ha='center',
        va='center',
        xytext=(0, 5),
        textcoords='offset points'
    )

# Create a legend mapping numbers to texts
legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                             label=f"{i+1}: {text[:30] + '...' if len(text) > 30 else text}",
                             markerfacecolor='grey', markersize=8) 
                  for i, text in enumerate(texts)]

# Add a second legend for text descriptions
second_legend = plt.legend(handles=legend_elements, title="Text References", 
                          loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=8)
plt.gca().add_artist(second_legend)

plt.title('Text Embeddings (OpenAI) with UMAP & HDBSCAN')
plt.xlabel('UMAP Dimension 1')
plt.ylabel('UMAP Dimension 2')
plt.legend(title="Clusters", loc='upper left', bbox_to_anchor=(1.01, 0.3))
plt.tight_layout()
plt.savefig('text_cluster_visualization.png', dpi=300, bbox_inches='tight')
plt.show()

# Print cluster assignments
print("\nCluster assignments:")
for i, (text, label) in enumerate(zip(texts, cluster_labels)):
    status = "Noise" if label == -1 else f"Cluster {label+1}"
    print(f"{i+1}: {text[:50]}{'...' if len(text) > 50 else ''} -> {status}")

# Analyze cluster themes (basic implementation)
print("\nCluster themes:")
clusters = {}
for label in unique_labels:
    if label != -1:  # Skip noise points
        indices = np.where(cluster_labels == label)[0]
        cluster_texts = [texts[i] for i in indices]
        clusters[f"Cluster {label+1}"] = cluster_texts
        
        print(f"\nCluster {label+1} texts:")
        for text in cluster_texts:
            print(f"- {text}")