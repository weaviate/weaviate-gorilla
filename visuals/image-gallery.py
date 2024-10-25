import streamlit as st
import os
import json
from PIL import Image

# Set the page title
st.set_page_config(page_title="Gorilla Image Gallery", layout="wide")

# Title for the gallery
st.title("Gorilla Image Gallery")

# Path to the image directory
image_dir = "weaviate-gorillas/"

# Get all image files from the directory
image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

# Initialize scores in session state if not already present
if 'image_scores' not in st.session_state:
    st.session_state.image_scores = {image: 0 for image in image_files}

# Function to update score
def update_score(image, score):
    st.session_state.image_scores[image] = score

# Function to save scores to disk
def save_scores():
    with open('image_scores.json', 'w') as f:
        json.dump(st.session_state.image_scores, f)
    st.success("Scores saved successfully!")

# Sort images by score
sorted_images = sorted(image_files, key=lambda x: st.session_state.image_scores[x], reverse=True)

# Create a grid layout
cols = st.columns(3)  # You can adjust the number of columns as needed

# Display images in the grid
for idx, image_file in enumerate(sorted_images):
    with cols[idx % 3]:
        image_path = os.path.join(image_dir, image_file)
        image = Image.open(image_path)
        st.image(image, caption=image_file, use_column_width=True)
        
        # Add a slider for scoring
        score = st.slider(f"Score for {image_file}", 0, 10, st.session_state.image_scores[image_file], key=f"slider_{image_file}")
        
        # Update score when slider value changes
        if score != st.session_state.image_scores[image_file]:
            update_score(image_file, score)

# Add a note about the number of images
st.write(f"Total images: {len(image_files)}")

# Display current scores
st.write("Current Scores:")
for image, score in st.session_state.image_scores.items():
    st.write(f"{image}: {score}")

# Add a button to save scores
if st.button("Save Scores"):
    save_scores()
