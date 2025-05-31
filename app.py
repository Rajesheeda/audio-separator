from flask import Flask, request, render_template, jsonify
from tasks import separate_audio_task

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    path = f'uploads/{file.filename}'
    file.save(path)

    task = separate_audio_task.delay(path)
    return jsonify({"task_id": task.id})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

