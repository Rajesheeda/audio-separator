import os
import subprocess
import uuid
import traceback
from flask import Flask, request, render_template, send_from_directory, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'separated'  # Demucs outputs go here
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Run Demucs with two stems: vocals and no_vocals
        result = subprocess.run(
            ["python3", "-m", "demucs", "--two-stems=vocals", filepath],
            capture_output=True, text=True
        )
        print("Demucs stdout:", result.stdout)
        print("Demucs stderr:", result.stderr)

        # Build path to separated outputs
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        output_subdir = os.path.join(OUTPUT_FOLDER, "htdemucs", base_name)

        vocals_file = os.path.join(output_subdir, 'vocals.wav')
        no_vocals_file = os.path.join(output_subdir, 'no_vocals.wav')

        if not os.path.exists(vocals_file) or not os.path.exists(no_vocals_file):
            return jsonify({"error": "Separation failed"}), 500

        # Return playback page
        return render_template('result.html',
                               vocals_play=f"/output/htdemucs/{base_name}/vocals.wav",
                               music_play=f"/output/htdemucs/{base_name}/no_vocals.wav")

    except Exception:
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
