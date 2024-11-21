from flask import Flask, render_template, request, redirect, url_for, flash
from PIL import Image, ImageChops
import hashlib
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

# Function to calculate the hash of an image
def calculate_hash(image_path):
    with open(image_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

# Function to check if the uploaded image is tampered
def check_tampering(uploaded_image_path):
    try:
        if not os.path.exists(ORIGINAL_IMAGE_PATH):
            return "Original image not found. Please upload it first."

        # Calculate hashes for comparison
        original_hash = calculate_hash(ORIGINAL_IMAGE_PATH)
        uploaded_hash = calculate_hash(uploaded_image_path)

        # Compare the hashes
        result = "Non-Tampered" if original_hash == uploaded_hash else "Tampered"
        log_result(uploaded_image_path, result)  # Log the result
        return result
    except Exception as e:
        return f"Error in tampering check: {e}"

# Function to log tampering results
def log_result(uploaded_image, result):
    with open("tampering_log.txt", "a") as log_file:
        log_file.write(f"File: {uploaded_image}, Result: {result}\n")

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
            # Save the original image with its filename
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"original_{file.filename}")
            file.save(original_path)
            flash(f"Original image {file.filename} uploaded successfully!")
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

@app.route('/download_original', methods=['GET'])
def download_original():
    if os.path.exists(ORIGINAL_IMAGE_PATH):
        return redirect(url_for('static', filename='uploads/original.jpg', _external=True))
    flash("Original image not found!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
