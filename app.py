import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io

# Function to load the color dataset
@st.cache_data
def load_color_dataset(file_path="colors.csv"):
    try:
        df = pd.read_csv(file_path="colors.csv")
        if not all(col in df.columns for col in ['name', 'red', 'green', 'blue']):
            st.error("Invalid color dataset format. Ensure columns: name, red, green, blue.")
            return None
        return df
    except FileNotFoundError:
        st.error("Color dataset (colors.csv) not found.")
        return None
    except Exception as e:
        st.error(f"Error loading color dataset: {e}")
        return None

# Function to find the closest color name
def find_closest_color(rgb, color_df):
    r, g, b = rgb
    distances = np.sqrt(
        (color_df['red'] - r) ** 2 +
        (color_df['green'] - g) ** 2 +
        (color_df['blue'] - b) ** 2
    )
    closest_idx = distances.idxmin()
    return color_df.loc[closest_idx, 'name']

# Streamlit app
def main():
    st.title("Color Detection Application")
    st.write("Upload an image and select a pixel to detect its color.")

    # Load color dataset
    color_df = load_color_dataset("colors.csv")
    if color_df is None:
        return

    # Image upload
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        try:
            # Read and display image
            image = Image.open(uploaded_file)
            img_array = np.array(image)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Display image with dimensions
            st.image(image, caption=f"Image (Width: {img_array.shape[1]}px, Height: {img_array.shape[0]}px)", use_column_width=True)
            
            # Coordinate input for pixel selection
            st.write("Enter X and Y coordinates to select a pixel (from top-left corner):")
            col1, col2 = st.columns(2)
            with col1:
                x_coord = st.number_input("X coordinate", min_value=0, max_value=img_array.shape[1]-1, value=0, step=1)
            with col2:
                y_coord = st.number_input("Y coordinate", min_value=0, max_value=img_array.shape[0]-1, value=0, step=1)
            
            if st.button("Detect Color"):
                if 0 <= x_coord < img_array.shape[1] and 0 <= y_coord < img_array.shape[0]:
                    # Get RGB values
                    b, g, r = img_bgr[y_coord, x_coord]
                    rgb = (r, g, b)
                    color_name = find_closest_color(rgb, color_df)
                    
                    # Display results
                    st.subheader("Detected Color")
                    st.write(f"**RGB Values**: ({r}, {g}, {b})")
                    st.write(f"**Color Name**: {color_name}")
                    
                    # Display color rectangle
                    color_box = np.zeros((100, 100, 3), dtype=np.uint8)
                    color_box[:] = [b, g, r]
                    color_box_rgb = cv2.cvtColor(color_box, cv2.COLOR_BGR2RGB)
                    st.image(color_box_rgb, caption="Detected Color", width=100)
                else:
                    st.error("Coordinates out of image bounds.")
        except Exception as e:
            st.error(f"Error processing image: {e}")

if __name__ == "__main__":
    main()
