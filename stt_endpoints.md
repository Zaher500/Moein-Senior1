# Quiz Generator Service Endpoints

Base path: `https://marielle-subchondral-rex.ngrok-free.dev/quiz/`

---

## Generate Quiz from File

- Method: `POST`
- URL: `https://marielle-subchondral-rex.ngrok-free.dev/quiz/generate/file/`
- Headers:
  - `Content-Type`: `multipart/form-data`
  - `X-Student-ID`: `<student_id>`
- Body: multipart/form-data
  - `file`: <PDF or DOCX file>
  - `lecture_id`: `<lecture_uuid>`
  - `course_id`: `<course_uuid>`
  - `num_questions`: `<integer>` (optional, default 5)
  - `title`: `<string>` (optional)

### Example response
```json
{
  "success": true,
  "message": "Quiz generated successfully",
  "data": {
    "quiz_id": "<quiz_uuid>",
    "status": "READY",
    "generated_count": 5
  }
}
```

---

## Generate Quiz from Existing Lecture File

- Method: `POST`
- URL: `https://marielle-subchondral-rex.ngrok-free.dev/quiz/generate/existing/`
- Headers:
  - `Content-Type`: `application/json`
  - `X-Student-ID`: `<student_id>`
- Body:
```json
{
  "lecture_id": "<lecture_uuid>",
  "course_id": "<course_uuid>",
  "num_questions": 5,
  "title": "Generated Quiz"
}
```

### Example response
```json
{
  "success": true,
  "message": "Quiz generated successfully",
  "data": {
    "quiz_id": "<quiz_uuid>",
    "status": "READY",
    "generated_count": 5
  }
}
```

---

## Generate Quiz from Scope

- Method: `POST`
- URL: `https://marielle-subchondral-rex.ngrok-free.dev/quiz/generate/scope/`
- Headers:
  - `Content-Type`: `application/json`
  - `X-Student-ID`: `<student_id>`
- Body:
```json
{
  "lecture_id": "<lecture_uuid>",
  "course_id": "<course_uuid>",
  "scope": "<scope_text>",
  "num_questions": 5,
  "title": "Generated Quiz"
}
```

### Example response
```json
{
  "success": true,
  "message": "Quiz generated successfully",
  "data": {
    "quiz_id": "<quiz_uuid>",
    "status": "READY",
    "generated_count": 5
  }
}
```

---

## Get Quiz Details

- Method: `GET`
- URL: `https://marielle-subchondral-rex.ngrok-free.dev/quiz/<quiz_id>/`
- Headers:
  - `Accept`: `application/json`

### Example response
```json
{
  "success": true,
  "message": "Quiz fetched successfully",
  "data": {
    "quiz_id": "<quiz_uuid>",
    "lecture_id": "<lecture_uuid>",
    "course_id": "<course_uuid>",
    "student_id": "<student_uuid>",
    "title": "Generated Quiz",
    "status": "READY",
    "num_questions": 5,
    "questions": [ ... ]
  }
}
```

---

## Get Quiz Status

- Method: `GET`
- URL: `https://marielle-subchondral-rex.ngrok-free.dev/quiz/<quiz_id>/status/`
- Headers:
  - `Accept`: `application/json`

### Example response
```json
{
  "success": true,
  "message": "Quiz status fetched",
  "data": {
    "quiz_id": "<quiz_uuid>",
    "status": "READY",
    "error": null
  }
}
```

---

## Submit Quiz Answers

- Method: `POST`
- URL: `https://marielle-subchondral-rex.ngrok-free.dev/quiz/<quiz_id>/submit/`
- Headers:
  - `Content-Type`: `application/json`
  - `X-Student-ID`: `<student_id>`
- Body:
```json
{
  "answers": [
    {
      "question_id": "<question_uuid>",
      "selected_answer": "<answer_text>"
    }
  ]
}
```

### Example response
```json
{
  "success": true,
  "message": "Quiz submitted successfully",
  "data": {
    "attempt_id": "<attempt_uuid>",
    "score": 4,
    "total": 5,
    "percentage": 80.0,
    "results": [ ... ]
  }
}
```

---

## Get Quizzes by Lecture

- Method: `GET`
- URL: `https://marielle-subchondral-rex.ngrok-free.dev/quiz/lecture/<lecture_id>/`
- Headers:
  - `Accept`: `application/json`

### Example response
```json
{
  "success": true,
  "message": "Lecture quizzes fetched successfully",
  "data": [ ... ]
}
```
```}