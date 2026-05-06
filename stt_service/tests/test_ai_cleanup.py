from types import SimpleNamespace
from unittest.mock import patch

from stt.ai_cleanup import (
    build_cleanup_prompt,
    clean_long_transcript_with_qwen_client,
    clean_transcript_with_qwen_client,
    split_text_into_chunks,
)


def test_build_cleanup_prompt_contains_raw_text():
    raw_text = "هذا نص خام"
    prompt = build_cleanup_prompt(raw_text)

    assert "Raw transcript:" in prompt
    assert raw_text in prompt
    assert "Do NOT summarize" in prompt


def test_clean_transcript_with_qwen_client_returns_empty_string_for_blank_input():
    assert clean_transcript_with_qwen_client("") == ""
    assert clean_transcript_with_qwen_client("   ") == ""


@patch("stt.ai_cleanup.hf_client")
def test_clean_transcript_with_qwen_client_returns_cleaned_text(mock_hf_client):
    mock_hf_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="نص منظف")
            )
        ]
    )

    result = clean_transcript_with_qwen_client("نص خام")

    assert result == "نص منظف"
    mock_hf_client.chat.completions.create.assert_called_once()


@patch("stt.ai_cleanup.hf_client")
def test_clean_transcript_with_qwen_client_falls_back_to_raw_text_when_response_empty(mock_hf_client):
    mock_hf_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="   ")
            )
        ]
    )

    raw_text = "نص خام"
    result = clean_transcript_with_qwen_client(raw_text)

    assert result == raw_text


@patch("stt.ai_cleanup.hf_client")
def test_clean_transcript_with_qwen_client_returns_raw_text_on_402_error(mock_hf_client):
    mock_hf_client.chat.completions.create.side_effect = Exception("402 Payment Required")

    raw_text = "نص خام"
    result = clean_transcript_with_qwen_client(raw_text)

    assert result == raw_text


@patch("stt.ai_cleanup.hf_client")
def test_clean_transcript_with_qwen_client_returns_raw_text_on_general_error(mock_hf_client):
    mock_hf_client.chat.completions.create.side_effect = Exception("Some network error")

    raw_text = "نص خام"
    result = clean_transcript_with_qwen_client(raw_text)

    assert result == raw_text


def test_split_text_into_chunks_returns_empty_list_for_blank_text():
    assert split_text_into_chunks("") == []
    assert split_text_into_chunks("   ") == []


def test_split_text_into_chunks_splits_long_text():
    text = "word1 word2 word3 word4 word5"
    chunks = split_text_into_chunks(text, max_chars=11)

    assert len(chunks) >= 2
    assert " ".join(chunks).replace("  ", " ").strip() == text


def test_split_text_into_chunks_does_not_exceed_max_chars_when_possible():
    text = "aaa bbb ccc ddd"
    chunks = split_text_into_chunks(text, max_chars=7)

    assert chunks == ["aaa", "bbb", "ccc", "ddd"]


@patch("stt.ai_cleanup.clean_transcript_with_qwen_client")
def test_clean_long_transcript_with_qwen_client_cleans_each_chunk(mock_clean_chunk):
    mock_clean_chunk.side_effect = lambda text: f"CLEAN[{text}]"

    raw_text = "part1 part2 part3 part4"
    result = clean_long_transcript_with_qwen_client(raw_text)

    assert "CLEAN[" in result
    assert mock_clean_chunk.called


@patch("stt.ai_cleanup.split_text_into_chunks", return_value=[])
def test_clean_long_transcript_with_qwen_client_returns_empty_string_when_no_chunks(mock_split):
    result = clean_long_transcript_with_qwen_client("")

    assert result == ""
    mock_split.assert_called_once()