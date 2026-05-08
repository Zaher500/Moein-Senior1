def get_user_from_headers(request):
    headers = request.META

    return {
        "student_id": headers.get("HTTP_X_STUDENT_ID"),
        "user_id": headers.get("HTTP_X_USER_ID"),
        "username": headers.get("HTTP_X_USERNAME"),
    }