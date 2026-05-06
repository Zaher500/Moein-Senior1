# Performance Test Report – STT Upload Endpoint

## Tested Endpoint
POST /stt/upload/

## Tool Used
k6

## Test Configuration
- Virtual Users (VUs): 5
- Duration: 20 seconds
- Scenario: constant VUs
- Uploaded file: audio file via multipart/form-data

## Results
- Total requests: 90
- Success rate: 100%
- Failure rate: 0%
- Average response time: 137.87 ms
- Median response time: 136.94 ms
- P90 response time: 151.68 ms
- P95 response time: 168.2 ms
- Maximum response time: 185.73 ms
- Throughput: 4.38 requests/sec

## Interpretation
The STT upload endpoint performed reliably under the tested load. All requests returned the expected HTTP 202 Accepted response, which confirms that the asynchronous upload-and-queue flow is functioning correctly.

The measured response times are relatively low because the endpoint does not perform transcription synchronously. Instead, it saves the uploaded file, creates a job record, and pushes the task to RabbitMQ for background processing.

## Conclusion
The upload endpoint is stable and responsive under moderate concurrent load. This supports the suitability of the current asynchronous architecture for speech-to-text job submission.