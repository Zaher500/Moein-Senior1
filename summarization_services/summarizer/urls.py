from django.urls import path
from .views import LectureTextAPIView, SummaryWordExportAPIView ,SummaryPDFExportAPIView
from .views import SummaryRetrieveAPIView, SummaryStatusAPIView

urlpatterns = [
    path('lecture-text/', LectureTextAPIView.as_view()),
    path("summary/status/<str:lecture_id>/", SummaryStatusAPIView.as_view()),
    path("summary/<str:lecture_id>/", SummaryRetrieveAPIView.as_view()),
    path("summary/<str:lecture_id>/pdf/", SummaryPDFExportAPIView.as_view()),
    path("summary/<str:lecture_id>/word/", SummaryWordExportAPIView.as_view()),

]