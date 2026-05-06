from django.urls import path
from .views import upload_audio_view,get_transcript_status_view

urlpatterns = [
  
    path('upload/', upload_audio_view, name='upload-audio'),
    path("stt-status/<str:job_id>/", get_transcript_status_view, name="stt_status"),

]