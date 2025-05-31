from flask import Flask, request, render_template
from concurrent.futures import ThreadPoolExecutor
import os
from spleeter.separator import Separator

from flask import send_from_directory

app = Flask(__name__)
executor = ThreadPoolExecutor()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["audio_file"]
        if file:
            upload_path = os.path.join("uploads", file.filename)
            file.save(upload_path)
            executor.submit(separate_audio, upload_path)
            return "Processing started. Check back later."
    return render_template("index.html")


@app.route('/output/<path:filename>')
def output_file(filename):
    return send_from_directory('output', filename)
    
def separate_audio(file_path):
    separator = Separator("spleeter:2stems")
    separator.separate_to_file(file_path, "outputs")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

