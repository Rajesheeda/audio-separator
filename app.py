import os
from flask import Flask, request, render_template, send_from_directory, send_file
from spleeter.separator import Separator
from werkzeug.utils import secure_filename
from pydub import AudioSegment

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
        return 'No file uploaded'
    
    file = request.files['file']
    if file.filename == '':
        return 'Empty filename'

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Spleeter separation
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(input_path, OUTPUT_FOLDER)

    filename_wo_ext = os.path.splitext(file.filename)[0]
    separated_folder = os.path.join(OUTPUT_FOLDER, filename_wo_ext)
    vocals_path = os.path.join(separated_folder, 'vocals.wav')
    accompaniment_path = os.path.join(separated_folder, 'accompaniment.wav')

    return render_template('result.html',
                           vocals_path=f"/download?v={vocals_path}",
                           music_path=f"/download?v={accompaniment_path}")

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/download')
def download():
    path = request.args.get('v')
    if not path or not os.path.exists(path):
        return 'File not found', 404
    return send_file(path, as_attachment=True)

    
@app.route('/output/<path:filename>')
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
