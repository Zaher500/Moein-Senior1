from unittest.mock import patch

from stt.consumer import process_audio_job


@patch("stt.consumer.clean_long_transcript_with_qwen_client")
@patch("stt.consumer.transcribe_audio")
def test_process_audio_job_lightweight(
    mock_transcribe,
    mock_clean,
):
    # Arrange
    mock_transcribe.return_value = "نص خام"
    mock_clean.return_value = "نص منظف"

    # Act
    result = process_audio_job("/fake/path/audio.wav")

    # Assert
    assert result == {
        "raw_transcript": "نص خام",
        "cleaned_transcript": "نص منظف",
    }

    mock_transcribe.assert_called_once_with("/fake/path/audio.wav")
    mock_clean.assert_called_once_with("نص خام")