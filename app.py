import os
from flask import Flask, request, render_template, send_from_directory
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    # Output directory for Spleeter
    output_subdir = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0])
    os.makedirs(output_subdir, exist_ok=True)

    # Run Spleeter
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(upload_path, OUTPUT_FOLDER)

    return render_template('result.html',
                           original_file=f"/{upload_path}",
                           vocals_file=f"/{output_subdir}/vocals.wav",
                           accompaniment_file=f"/{output_subdir}/accompaniment.wav")

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/output/<path:filename>')
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
