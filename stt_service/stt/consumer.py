import json
import os
import time
import tempfile
import numpy as np
import noisereduce as nr
import pika
from django.conf import settings
from faster_whisper import WhisperModel
from pydub import AudioSegment
from stt.mongo_store import update_job_status, save_job_result, mark_job_failed
from stt.ai_cleanup import clean_long_transcript_with_qwen_client
from stt.notification_producer import send_notification


# ==============================
# Windows / environment setup
# ==============================
os.environ["PATH"] += r";C:\ffmpeg\ffmpeg-8.1-essentials_build\bin"
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


# ==============================
# Settings
# ==============================
LANGUAGE = "ar"
BEAM_SIZE = 5

DEVICE = "cuda"
COMPUTE_TYPE = "int8_float16"

TARGET_SAMPLE_RATE = 16000
HIGH_PASS_HZ = 100
LOW_PASS_HZ = 7800
NOISE_REDUCTION_STRENGTH = 0.75


# ==============================
# Load Whisper model once
# ==============================
print("Loading faster-whisper model...")
model = WhisperModel(
    "medium",
    device=DEVICE,
    compute_type=COMPUTE_TYPE,
    download_root="models",
)
print("faster-whisper model loaded")


# ==============================
# Audio preprocessing
# ==============================
def preprocess_audio(local_file_path: str) -> str:
    print("Preprocessing audio...")

    audio = AudioSegment.from_file(local_file_path)

    audio = audio.set_channels(1).set_frame_rate(TARGET_SAMPLE_RATE) 
    audio = audio.normalize()
    audio = audio.high_pass_filter(HIGH_PASS_HZ)
    audio = audio.low_pass_filter(LOW_PASS_HZ)

    samples = np.array(audio.get_array_of_samples()).astype(np.float32)

    max_val = float(1 << (8 * audio.sample_width - 1))
    if max_val > 0:
        samples = samples / max_val
       
    reduced_noise = nr.reduce_noise(
        y=samples,
        sr=TARGET_SAMPLE_RATE,
        stationary=False,
        prop_decrease=NOISE_REDUCTION_STRENGTH,
    )

    reduced_noise = np.clip(reduced_noise, -1.0, 1.0)
    reduced_int16 = (reduced_noise * 32767).astype(np.int16)

    clean_audio = AudioSegment(
        reduced_int16.tobytes(),
        frame_rate=TARGET_SAMPLE_RATE,
        sample_width=2,
        channels=1,
    )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        clean_path = tmp_file.name

    clean_audio.export(clean_path, format="wav")
    print(f"Preprocessing done: {clean_path}")

    return clean_path


# ==============================
# Speech-to-text
# ==============================
def transcribe_audio(local_file_path: str) -> str:
    clean_path = preprocess_audio(local_file_path)

    try:
        print("Starting transcription...")

        segments, info = model.transcribe(
            clean_path,
            language=LANGUAGE,
            beam_size=BEAM_SIZE,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=400
            ),
            word_timestamps=False,
        )

        texts = []
        for segment in segments:
            text = (segment.text or "").strip()
            if text:
                texts.append(text)

        return " ".join(texts).strip()

    finally:
        if os.path.exists(clean_path):
            os.remove(clean_path)
            print(f"Deleted temp clean file: {clean_path}")


# ==============================
# Full processing pipeline
# ==============================
def process_audio_job(local_file_path: str) -> dict:
    raw_transcript = transcribe_audio(local_file_path)
    cleaned_transcript = clean_long_transcript_with_qwen_client(raw_transcript)

    return {
        "raw_transcript": raw_transcript,
        "cleaned_transcript": cleaned_transcript,
    }

# ==============================
# Helper for notifications
# ==============================
def safe_send_notification(user_id, message, notif_type):
    try:
        send_notification(user_id, message, notif_type)
    except Exception as e:
        print(f"Notification failed: {e}")


# ==============================
# RabbitMQ callback
# ==============================
def callback(ch, method, properties, body):
    job_id = None
    user_id = None

    try:
        message = json.loads(body)

        job_id = message["job_id"]
        local_file_path = message["local_file_path"]
        original_file_name = message.get("original_file_name", "unknown")
        user_id = message.get("user_id")

        update_job_status(job_id, "processing")

        if user_id:
            safe_send_notification(
                user_id,
                "the audio is processing",
                "transcribe"
            )

        print("==========================================")
        print("Received job from RabbitMQ")
        print(f"Job ID: {job_id}")
        print(f"Original file name: {original_file_name}")
        print(f"Local file path: {local_file_path}")
        print("==========================================")

        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Audio file not found: {local_file_path}")

        result = process_audio_job(local_file_path)

        raw_transcript = result["raw_transcript"]
        cleaned_transcript = result["cleaned_transcript"]

        save_job_result(
            job_id=job_id,
            raw_transcript=raw_transcript,
            cleaned_transcript=cleaned_transcript,
        )

        if user_id:
            safe_send_notification(
                user_id,
                "the audio is completed",
                "transcribe"
            )

        print("==========================================")
        print(f"DONE Job: {job_id}")
        print("==========================================")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        if job_id:
            mark_job_failed(job_id, str(e))

        if user_id:
            safe_send_notification(
                user_id,
                "the audio failed to process",
                "transcribe"
            )

        print("==========================================")
        print(f"ERROR: {str(e)}")
        print("==========================================")

        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
# ==============================
# Start consumer
# ==============================
def start_consumer():
    while True:
        try:
            rabbitmq_host = settings.RABBITMQ_HOST
            rabbitmq_queue = settings.RABBITMQ_QUEUE

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbitmq_host,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
            )

            channel = connection.channel()
            channel.queue_declare(queue=rabbitmq_queue, durable=True)
            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(
                queue=rabbitmq_queue,
                on_message_callback=callback,
                auto_ack=False,
            )

            print("Waiting for STT jobs...")
            channel.start_consuming()

        except AttributeError as e:
            print(f"Settings error: {e}")
            break

        except Exception as e:
            print(f"RabbitMQ / runtime error: {e}")
            print("Reconnecting in 5 seconds...")
            time.sleep(5)
if __name__ == "__main__":
    start_consumer()