import os
from flask import Flask, request, render_template, send_file, session
from spleeter.separator import Separator
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import secrets

# Flask setup
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key

# Directories
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Routes
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return 'No file uploaded'
    
    file = request.files['file']
    if file.filename == '':
        return 'Empty filename'

    # Save uploaded file
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    # Run Spleeter (2 stems: vocals + accompaniment)
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(input_path, OUTPUT_FOLDER)

    # File paths
    filename_wo_ext = os.path.splitext(filename)[0]
    separated_folder = os.path.join(OUTPUT_FOLDER, filename_wo_ext)
    vocals_path = os.path.join(separated_folder, 'vocals.wav')
    accompaniment_path = os.path.join(separated_folder, 'accompaniment.wav')

    # Pass paths to session or context
    return render_template('result.html',
                           vocals_path=f"/download?v={vocals_path}",
                           music_path=f"/download?v={accompaniment_path}",
                           vocals_play=f"/stream?v={vocals_path}",
                           music_play=f"/stream?v={accompaniment_path}"
                           )

@app.route('/download')
def download():
    path = request.args.get('v')
    if not path or not os.path.exists(path):
        return 'File not found', 404
    return send_file(path, as_attachment=True)

@app.route('/stream')
def stream():
    path = request.args.get('v')
    if not path or not os.path.exists(path):
        return 'File not found', 404
    return send_file(path)

if __name__ == '__main__':
    app.run(debug=True)
