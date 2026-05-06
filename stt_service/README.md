# STT Service Testing Project

## Overview

This repository contains the testing and CI/CD implementation for the Speech-to-Text (STT) microservice of the Moein AI Student Assistant project.

The project focuses on validating the STT upload and transcript workflow using multiple software testing approaches and an automated DevOps pipeline.

---

## Implemented Testing Types

### 1. Unit Testing

Implemented using **Pytest** for isolated components.

Covered modules:

* `views.py`
* `mongo_store.py`
* `producer.py`
* `ai_cleanup.py`

Run locally:

```bash
pytest tests -v
```

### 2. Integration Testing

Tested the complete backend flow:

* Upload audio file
* Create transcription job
* Send job to queue
* Retrieve transcript status

File:

```text
tests/test_integration_stt.py
```

### 3. Performance Testing

Implemented using **k6**.

Scenario tested:

* Concurrent users upload audio files
* Endpoint tested: `POST /stt/upload/`

Run locally:

```bash
k6 run performance/stt_upload_test.js
```

Latest Results:

* Checks Passed: 100%
* Request Failures: 0%
* Average Response Time: ~123 ms
* Successful handling of concurrent requests

### 4. End-to-End Testing (E2E)

Implemented using **Playwright**.

Scenario:

* User login
* Navigate to Transcribe page
* Upload audio file
* Verify queued transcript job

---

## CI/CD Pipeline

Implemented using **GitHub Actions**.

Pipeline runs automatically on every push / pull request.

Included Jobs:

* **Run Tests** → Unit + Integration tests
* **Run Performance Test** → Starts backend service and runs k6
* **Run GitLeaks Security Scan** → Detects leaked secrets / tokens

---

## Security

Implemented using **GitLeaks**.

Detects:

* API Keys
* Tokens
* Credentials
* Sensitive data accidentally committed

---

## Technologies Used

* Python
* Django
* Pytest
* GitHub Actions
* k6
* Playwright
* GitLeaks
* RabbitMQ
* MongoDB

---

## Team Members

* محمد يحيى ابو سمرة 
    محمد اواب خير 

---

## Repository Purpose

This repository was created to fulfill the Software Testing & DevOps assignment requirements through a real-world microservice testing case study.

---

## Final Status

1. CI/CD Pipeline
2. Unit Testing
3. Integration Testing
4. Performance Testing
5. E2E Testing
6. Security Scanning
