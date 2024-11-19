from flask import Flask, render_template, request, redirect, url_for, flash
from PIL import Image, ImageChops
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ORIGINAL_IMAGE_PATH = os.path.join(UPLOAD_FOLDER, 'original.jpg')

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the uploaded image is tampered
def check_tampering(uploaded_image_path):
    try:
        # Load the original and uploaded images
        if not os.path.exists(ORIGINAL_IMAGE_PATH):
            return "Original image not found. Please upload it first."

        original = Image.open(ORIGINAL_IMAGE_PATH)
        uploaded = Image.open(uploaded_image_path)

        # Resize the uploaded image to match the original
        uploaded = uploaded.resize(original.size)

        # Compare the two images using pixel-by-pixel difference
        diff = ImageChops.difference(original, uploaded)

        # If there's a difference, the image is tampered
        if diff.getbbox():  # Bounding box indicates pixel differences
            return "Tampered"
        return "Non-Tampered"
    except Exception as e:
        return f"Error in tampering check: {e}"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_original', methods=['GET', 'POST'])
def upload_original():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part in the request.")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("No file selected for upload.")
            return redirect(request.url)

        if file:
            # Save the file as the original image
            file.save(ORIGINAL_IMAGE_PATH)
            flash("Original image uploaded successfully!")
            return redirect(url_for('index'))
    return render_template('upload_original.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part in the request.")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("No file selected for upload.")
            return redirect(request.url)

        if file:
            # Save the uploaded file
            uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(uploaded_path)

            # Check for tampering
            result = check_tampering(uploaded_path)

            # Pass the static path to the template
            return render_template('upload.html', result=result, image_url=f'uploads/{file.filename}')
    return render_template('upload_file.html')

if __name__ == '__main__':
    app.run(debug=True)
