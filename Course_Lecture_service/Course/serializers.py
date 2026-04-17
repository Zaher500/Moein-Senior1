from rest_framework import serializers
from .models import Course, Lecture
from .jwt_utils import get_student_id_from_token


class LectureCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for CREATING lectures (upload)
    """
    class Meta:
        model = Lecture
        fields = ['lecture_name']  # Only what user provides during upload
    
    def validate_lecture_name(self, value):
        if len(value) > 200:
            raise serializers.ValidationError("Lecture name cannot exceed 200 characters.")
        return value

# serializers.py
class LectureSerializer(serializers.ModelSerializer):
    """
    Serializer for READING lectures (display)
    """
    course_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Lecture
        fields = [
            'lecture_id',
            'student_id',
            'course_id',
            'lecture_name',
            'summary_status',
            'course_info',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['lecture_id', 'student_id', 'course_id', 'created_at', 'updated_at']
    
    def get_course_info(self, obj):
        """Get minimal course info"""
        return {
            'course_id': str(obj.course_id.course_id),
            'course_name': obj.course_id.course_name
        }

# serializers.py
class CourseSerializer(serializers.ModelSerializer):
    lectures = serializers.SerializerMethodField()
    lecture_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'course_teacher', 'lectures', 'lecture_count', 'created_at']

    def get_student_id(self):
        request = self.context.get('request')
        if not request:
            return None
        return get_student_id_from_token(request)

    def get_lecture_count(self, obj):
        student_id = self.get_student_id()
        if not student_id:
            return 0
        return Lecture.objects.filter(course_id=obj, student_id=student_id).count()

    def get_lectures(self, obj):
        student_id = self.get_student_id()
        if not student_id:
            return []

        lectures = Lecture.objects.filter(course_id=obj, student_id=student_id)[:3]
        return [
            {
                'lecture_id': str(lecture.lecture_id),
                'lecture_name': lecture.lecture_name,
                'has_file': bool(lecture.file_name),
                'created_at': lecture.created_at
            }
            for lecture in lectures
        ]