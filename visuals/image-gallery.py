import streamlit as st
import os
from PIL import Image

# Set the page title
st.set_page_config(page_title="Gorilla Image Gallery", layout="wide")

# Title for the gallery
st.title("Gorilla Image Gallery")

# Path to the image directory
image_dir = "weaviate-gorillas/"

# Get all image files from the directory
image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

# Create a grid layout
cols = st.columns(3)  # You can adjust the number of columns as needed

# Display images in the grid
for idx, image_file in enumerate(image_files):
    with cols[idx % 3]:
        image_path = os.path.join(image_dir, image_file)
        image = Image.open(image_path)
        st.image(image, caption=image_file, use_column_width=True)

# Add a note about the number of images
st.write(f"Total images: {len(image_files)}")
