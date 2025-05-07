import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io
import base64

# Function to load the color dataset
@st.cache_data
def load_color_dataset(file_path="colors.csv"):
    try:
        df = pd.read_csv(file_path)
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

# Function to convert image to base64 for HTML display
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Streamlit app
def main():
    st.title("Color Detection Application")
    st.write("Upload an image and click on it to detect the color at that point.")

    # Load color dataset
    color_df = load_color_dataset()
    if color_df is None:
        return

    # Image upload
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        try:
            # Read and process image
            image = Image.open(uploaded_file)
            img_array = np.array(image)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Initialize session state for click coordinates
            if 'click_coords' not in st.session_state:
                st.session_state.click_coords = None

            # Convert image to base64 for HTML
            img_base64 = image_to_base64(image)

            # HTML and JavaScript for clickable image
            html_code = f"""
            <div>
                <img id="clickableImage" src="data:image/png;base64,{img_base64}" style="max-width: 100%; height: auto;" />
                <p>Click on the image to select a pixel.</p>
            </div>
            <script>
                const img = document.getElementById('clickableImage');
                img.addEventListener('click', function(e) {{
                    const rect = img.getBoundingClientRect();
                    const x = Math.round(e.clientX - rect.left);
                    const y = Math.round(e.clientY - rect.top);
                    // Send coordinates to Streamlit
                    window.parent.postMessage({{
                        type: 'streamlit:set_component_value',
                        value: {{x: x, y: y}}
                    }}, '*');
                }});
            </script>
            """
            st.markdown(html_code, unsafe_allow_html=True)

            # Custom component to capture click coordinates
            coords = st.experimental_get_query_params().get('coords', None)
            if coords:
                try:
                    x_coord, y_coord = map(int, coords[0].split(','))
                    st.session_state.click_coords = (x_coord, y_coord)
                except:
                    st.error("Invalid coordinates received.")

            # Display current coordinates
            if st.session_state.click_coords:
                x_coord, y_coord = st.session_state.click_coords
                st.write(f"Selected Coordinates: X={x_coord}, Y={y_coord}")
                
                # Validate coordinates and detect color
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
