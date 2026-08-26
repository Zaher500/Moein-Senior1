import json
from unittest.mock import MagicMock, patch

from stt.producer import send_job_to_queue


@patch("stt.producer.pika.BlockingConnection")
@patch("stt.producer.settings")
def test_send_job_to_queue_publishes_durable_message(mock_settings, mock_blocking_connection):
    mock_settings.RABBITMQ_HOST = "localhost"
    mock_settings.RABBITMQ_QUEUE = "stt_jobs"

    mock_connection = MagicMock()
    mock_channel = MagicMock()

    mock_blocking_connection.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    payload = {
        "job_id": "job-123",
        "local_file_path": "/tmp/job-123.wav",
        "original_file_name": "lecture.wav",
    }

    send_job_to_queue(payload)

    mock_blocking_connection.assert_called_once()
    mock_connection.channel.assert_called_once()

    mock_channel.queue_declare.assert_called_once_with(
        queue="stt_jobs",
        durable=True,
    )

    mock_channel.basic_publish.assert_called_once()
    publish_kwargs = mock_channel.basic_publish.call_args.kwargs

    assert publish_kwargs["exchange"] == ""
    assert publish_kwargs["routing_key"] == "stt_jobs"
    assert json.loads(publish_kwargs["body"]) == payload
    assert publish_kwargs["properties"].delivery_mode == 2

    mock_connection.close.assert_called_once()


@patch("stt.producer.pika.BlockingConnection")
@patch("stt.producer.settings")
def test_send_job_to_queue_uses_rabbitmq_host_from_settings(mock_settings, mock_blocking_connection):
    mock_settings.RABBITMQ_HOST = "rabbitmq-service"
    mock_settings.RABBITMQ_QUEUE = "audio_queue"

    mock_connection = MagicMock()
    mock_channel = MagicMock()

    mock_blocking_connection.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    payload = {"job_id": "job-999"}

    send_job_to_queue(payload)

    connection_params = mock_blocking_connection.call_args.args[0]
    assert connection_params.host == "rabbitmq-service"

    publish_kwargs = mock_channel.basic_publish.call_args.kwargs
    assert publish_kwargs["routing_key"] == "audio_queue"
    assert json.loads(publish_kwargs["body"]) == payload