from rest_framework import serializers
from .models import Summary



class LectureTextSerializer(serializers.Serializer):
    lecture_id = serializers.CharField()
    text = serializers.CharField()

    def to_internal_value(self, data):
        data = data.copy()

        if "text" in data and isinstance(data["text"], str):
            data["text"] = (
                data["text"]
                .replace('\x00', '')
                .replace('\u0000', '')
            )

        return super().to_internal_value(data)


# للقراءة فقط
class SummaryTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ['summary_text']  # بس النص الملخص
