# Color Detection Application

A Streamlit-based web application that allows users to upload an image, select a pixel by entering coordinates, and detect the color at that point. The app displays the RGB values, the closest matching color name from a dataset, and a visual rectangle filled with the detected color.

## Features
- Upload images (JPG, PNG, JPEG).
- Detect RGB values at a specified pixel.
- Match the RGB values to the closest color name using a CSV dataset.
- Display a visual box filled with the detected color.
- Error handling for invalid inputs or missing datasets.

## Prerequisites
- Python 3.8 or higher
- Git
- Streamlit Community Cloud account (for deployment)

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/color-detection-app.git
   cd color-detection-app
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application Locally**:
   ```bash
   streamlit run app.py
   ```
   Open your browser to `http://localhost:8501`.

## Deployment on Streamlit Community Cloud
1. Push the repository to GitHub.
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Create a new app, linking it to your GitHub repository.
4. Specify `app.py` as the main script and ensure `requirements.txt` is included.
5. Deploy the app and access it via the provided URL.

## Project Structure
- `app.py`: Main Streamlit application script.
- `colors.csv`: Dataset with color names and RGB values.
- `requirements.txt`: List of Python dependencies.
- `README.md`: Project documentation.

## Usage
1. Upload an image using the file uploader.
2. Enter X and Y coordinates to select a pixel (from the top-left corner).
3. Click "Detect Color" to view the RGB values, color name, and a color-filled rectangle.

## Notes
- The app uses coordinate input for pixel selection due to Streamlit's lack of native image click event support.
- The `colors.csv` dataset can be extended with additional colors.
- Ensure the image is in a supported format (JPG, PNG, JPEG).

## Future Enhancements
- Add support for clicking directly on the image (requires custom JavaScript or a different framework).
- Include HEX code display alongside RGB values.
- Allow users to upload or extend the color dataset.
- Optimize for mobile devices.

## License
MIT License
