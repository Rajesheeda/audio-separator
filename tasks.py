import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "rediss://default:AaxkAAIjcDFlOTg0N2NjYWEzYWY0NjFlOGM5NWFmZTBhY2ZkZjg3NHAxMA@smiling-dolphin-44132.upstash.io:6379")

app = Celery('tasks', broker=redis_url)

@app.task
def separate_audio_task(file_path):
    from spleeter.separator import Separator
    import os

    separator = Separator('spleeter:2stems')
    separator.separate_to_file(file_path, 'outputs')

    base_path = f'outputs/{os.path.splitext(os.path.basename(file_path))[0]}'
    vocals_path = f'{base_path}/vocals.wav'
    instrumental_path = f'{base_path}/accompaniment.wav'
    
    return vocals_path, instrumental_path

