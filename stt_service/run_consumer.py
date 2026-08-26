import os
import django

# ربط Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stt_service.settings")
django.setup()

from stt.consumer import start_consumer

if __name__ == "__main__":
    start_consumer()