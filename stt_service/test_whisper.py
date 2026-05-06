import os
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from faster_whisper import WhisperModel

print("⏳ Loading model...")

model = WhisperModel(
    "medium",
     device="cpu",
    compute_type="int8",
    download_root="models"   # مهم جدًا
)

print("✅ Model loaded")

segments, info = model.transcribe(r"C:\Users\yahya\OneDrive\سطح المكتب\رؤية نظري محاضرة 2.m4a", language="ar")

print("================================")

for segment in segments:
    print(segment.text)