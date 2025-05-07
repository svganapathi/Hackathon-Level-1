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
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        st.error(f"Error encoding image to base64: {e}")
        return None

# Streamlit app
def main():
    st.title("Color Detection Application")
    st.write("Click anywhere on the image to detect the color at that point.")

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
            
            # Fallback: Display image using st.image to confirm it loads correctly
            st.image(image, caption="Uploaded Image (Fallback Display)", use_column_width=True)

            # Initialize session state for click coordinates
            if 'click_coords' not in st.session_state:
                st.session_state.click_coords = None
            if 'click_counter' not in st.session_state:
                st.session_state.click_counter = 0

            # Convert image to base64 for HTML
            img_base64 = image_to_base64(image)
            if img_base64 is None:
                return

            # HTML and JavaScript for clickable canvas
            html_code = f"""
            <div style="position: relative; display: inline-block;">
                <canvas id="imageCanvas" style="max-width: 100%; height: auto; cursor: crosshair;"></canvas>
                <canvas id="overlayCanvas" style="position: absolute; top: 0; left: 0; pointer-events: none;"></canvas>
            </div>
            <p>Click on the image to select a pixel. A yellow circle will mark the selected point.</p>
            <script>
                const canvas = document.getElementById('imageCanvas');
                const overlay = document.getElementById('overlayCanvas');
                const ctx = canvas.getContext('2d');
                const overlayCtx = overlay.getContext('2d');
                const img = new Image();
                img.src = 'data:image/png;base64,{img_base64}';
                img.onload = function() {{
                    canvas.width = img.width;
                    canvas.height = img.height;
                    overlay.width = img.width;
                    overlay.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    // Scale canvas to fit container
                    const scale = Math.min(1, canvas.parentElement.clientWidth / img.width);
                    canvas.style.width = (img.width * scale) + 'px';
                    canvas.style.height = (img.height * scale) + 'px';
                    overlay.style.width = (img.width * scale) + 'px';
                    overlay.style.height = (img.height * scale) + 'px';
                }};
                img.onerror = function() {{
                    console.error('Failed to load image on canvas');
                }};
                canvas.addEventListener('click', function(e) {{
                    const rect = canvas.getBoundingClientRect();
                    const scale = canvas.width / rect.width;
                    const x = Math.round((e.clientX - rect.left) * scale);
                    const y = Math.round((e.clientY - rect.top) * scale);
                    // Draw yellow circle
                    overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
                    overlayCtx.beginPath();
                    overlayCtx.arc(x, y, 5, 0, 2 * Math.PI);
                    overlayCtx.fillStyle = 'yellow';
                    overlayCtx.fill();
                    overlayCtx.strokeStyle = 'black';
                    overlayCtx.lineWidth = 1;
                    overlayCtx.stroke();
                    // Update hidden input for Streamlit
                    document.getElementById('coords').value = JSON.stringify({{x: x, y: y}});
                    // Trigger Streamlit rerun
                    const counter = parseInt(document.getElementById('counter').value || '0') + 1;
                    document.getElementById('counter').value = counter;
                    // Log for debugging
                    console.log('Clicked at: x=' + x + ', y=' + y);
                }});
            </script>
            <input type="hidden" id="coords" value="">
            <input type="hidden" id="counter" value="{st.session_state.click_counter}">
            """
            st.markdown(html_code, unsafe_allow_html=True)

            # Capture coordinates from hidden input
            coords_input = st.text_input("Coordinates (auto-updated)", key="coords_input", value="", disabled=True)
            counter = st.text_input("Click Counter (auto-updated)", key="counter_input", value=str(st.session_state.click_counter), disabled=True)

            if coords_input and counter != str(st.session_state.click_counter):
                st.session_state.click_counter = int(counter)
                try:
                    coords = eval(coords_input)
                    x_coord, y_coord = coords['x'], coords['y']
                    st.session_state.click_coords = (x_coord, y_coord)
                except:
                    st.error("Invalid coordinates received.")

            # Display and process clicked coordinates
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
