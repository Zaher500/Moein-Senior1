import uuid
from django.db import models

class Quiz(models.Model):
    SOURCE_CHOICES = [
        ('FILE', 'FILE'),
        ('EXISTING', 'EXISTING'),
        ('SCOPE', 'SCOPE'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('PROCESSING', 'PROCESSING'),
        ('READY', 'READY'),
        ('FAILED', 'FAILED'),
    ]

    quiz_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lecture_id = models.UUIDField(null=True, blank=True)
    course_id = models.UUIDField(null=True, blank=True)
    student_id = models.UUIDField()
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error = models.TextField(null=True, blank=True)
    num_questions = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.quiz_id})"

class Question(models.Model):
    TYPE_CHOICES = [
        ('MCQ', 'MCQ'),
        ('TRUE_FALSE', 'TRUE_FALSE'),
    ]

    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    question_text = models.TextField()
    options = models.CharField(max_length=1000, null=True, blank=True)
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Question {self.order} for Quiz {self.quiz_id}"

class QuizAttempt(models.Model):
    attempt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student_id = models.UUIDField()
    score = models.FloatField()
    total = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt by {self.student_id} on Quiz {self.quiz_id}"

class Answer(models.Model):
    answer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Answer {self.answer_id} for Attempt {self.attempt_id}"
