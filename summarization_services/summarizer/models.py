from django.db import models
import uuid

class Summary(models.Model):
    summary_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    lecture_id = models.CharField(max_length=255)
    summary_text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary {self.summary_id} for Lecture {self.lecture_id}"
