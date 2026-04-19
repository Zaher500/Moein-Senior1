from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.get_my_courses, name='get-my-courses'),
    path('courses/create/', views.create_course, name='create-course'),
    path('courses/<uuid:course_id>/', views.get_course, name='get-course'),
    path('courses/<uuid:course_id>/edit/', views.update_course, name='update-course'),
    path('courses/<uuid:course_id>/delete/', views.delete_course, name='delete-course'),
    path('courses/<uuid:course_id>/lectures/upload/', views.upload_lecture, name='upload-lecture'),
    path('courses/<uuid:course_id>/lectures/<uuid:lecture_id>/update-name/', views.update_lecture_name, name='update-lecture-name'),
    path('courses/<uuid:course_id>/lectures/<uuid:lecture_id>/delete/', views.delete_lecture, name='delete-lecture'),
    path('delete-student-courses/<uuid:student_id>/', views.delete_student_courses),
    path('courses/<uuid:course_id>/lectures/', views.get_course_lectures, name='get-course-lectures'),
    path('lectures/<uuid:lecture_id>/', views.get_lecture, name='get-lecture'),
    path('media/<uuid:student_id>/<uuid:course_id>/<path:filename>/', views.serve_media_file, name='serve-media'),
    path('lectures/<uuid:lecture_id>/summary/', views.get_lecture_summary, name='get-lecture-summary'),
    path('generate/existing/', views.get_lecture_file, name='get-lecture-file'),
    path('lectures/<uuid:lecture_id>/file/', views.get_lecture_file, name='get-lecture-file'),
]