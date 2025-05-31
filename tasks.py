import os
from dotenv import load_dotenv
from celery import Celery

# Load variables from .env file
load_dotenv()

# Get Redis URL from environment
redis_url = os.getenv("REDIS_URL")

app = Celery('tasks', broker=redis_url)

@app.task
def separate_audio_task(file_path):
    from spleeter.separator import Separator
    import os

    separator = Separator('spleeter:2stems')
    separator.separate_to_file(file_path, 'outputs')

    base = os.path.splitext(os.path.basename(file_path))[0]
    base_path = f'outputs/{base}'
    vocals = f'{base_path}/vocals.wav'
    instrumental = f'{base_path}/accompaniment.wav'

    return {'vocals': vocals, 'instrumental': instrumental}


