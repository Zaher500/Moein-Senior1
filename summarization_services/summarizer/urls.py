from django.urls import path
from .views import LectureTextAPIView
from .views import SummaryRetrieveAPIView, SummaryStatusAPIView

urlpatterns = [
    path('lecture-text/', LectureTextAPIView.as_view()),
    path("summary/status/<str:lecture_id>/", SummaryStatusAPIView.as_view()),
    path("summary/<str:lecture_id>/", SummaryRetrieveAPIView.as_view()),

]