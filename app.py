import os
import subprocess
import uuid
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
import traceback

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        uploaded_file = request.files['file']
        # Save file or process it
        uploaded_file.save('/tmp/' + uploaded_file.filename)
        return jsonify({"message": "File uploaded successfully"})
    except Exception as e:
        print(traceback.format_exc())  # Log full traceback to stdout/stderr (visible in logs)
        return jsonify({"error": str(e)}), 500
        

@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    # Save uploaded file
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    # Run Spleeter CLI (2 stems: vocals + accompaniment)
    try:
        subprocess.run([
            'spleeter', 'separate',
            '-p', 'spleeter:2stems',
            '-o', OUTPUT_FOLDER,
            input_path
        ], check=True)
    except subprocess.CalledProcessError:
        return "Audio processing failed", 500

    # Build output file paths
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.join(OUTPUT_FOLDER, base_name)

    vocals_path = os.path.join(output_dir, 'vocals.wav')
    music_path = os.path.join(output_dir, 'accompaniment.wav')

    # Return HTML with playback + download links
    return render_template('result.html',
        vocals_path=f'/{vocals_path}',
        music_path=f'/{music_path}',
        vocals_play=f'/{vocals_path}',
        music_play=f'/{music_path}'
    )

# Allow serving uploaded/processed files
@app.route('/uploads/<path:filename>')
def download_uploaded(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/output/<path:filename>')
def download_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
