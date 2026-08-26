from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SummaryTextSerializer
from .rabbitmq import send_to_queue
from .models import Summary
from .serializers import LectureTextSerializer
from rest_framework.decorators import api_view
from .db.mongo import get_summary_by_lecture_id, is_summary_ready


class LectureTextAPIView(APIView):
    def post(self, request):
        print("Summarization request received")
        serializer = LectureTextSerializer(data=request.data)

        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        lecture_id = serializer.validated_data["lecture_id"]
        text = serializer.validated_data["text"]

        text = text.replace("\x00", "").strip()

        send_to_queue({"lecture_id": lecture_id, "text": text})

        return Response(
            {"message": "Text received and sent to queue"},
            status=status.HTTP_202_ACCEPTED,
        )


class SummaryStatusAPIView(APIView):
    def get(self, request, lecture_id):
        ready = is_summary_ready(lecture_id)

        return Response(
            {"lecture_id": lecture_id, "ready": ready}, status=status.HTTP_200_OK
        )


class SummaryRetrieveAPIView(APIView):
    def get(self, request, lecture_id):
        summary_doc = get_summary_by_lecture_id(lecture_id)

        if not summary_doc:
            return Response(
                {"error": "Summary not ready", "lecture_id": lecture_id},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"lecture_id": lecture_id, "summary": summary_doc.get("summary_text")},
            status=status.HTTP_200_OK,
        )
