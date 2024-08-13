import pytest
from modules.jax.testcontainers.whisper_cuda.whisper_diarization import JAXWhisperDiarizationContainer


@pytest.fixture(scope="module")
def hf_token():
    return "your_huggingface_token_here"  # Replace with a valid token or use an environment variable


def test_jax_whisper_diarization_container(hf_token):
    with JAXWhisperDiarizationContainer(hf_token=hf_token) as whisper_diarization:
        whisper_diarization.connect()

        # Test file transcription and diarization
        result = whisper_diarization.transcribe_and_diarize_file("/path/to/test/audio.wav")
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        assert all("speaker" in item and "text" in item and "timestamp" in item for item in result)

        # Test YouTube transcription and diarization
        result = whisper_diarization.transcribe_and_diarize_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        assert all("speaker" in item and "text" in item and "timestamp" in item for item in result)


def test_jax_whisper_diarization_container_without_grouping(hf_token):
    with JAXWhisperDiarizationContainer(hf_token=hf_token) as whisper_diarization:
        whisper_diarization.connect()

        result = whisper_diarization.transcribe_and_diarize_file("/path/to/test/audio.wav", group_by_speaker=False)
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        assert all("speaker" in item and "text" in item and "timestamp" in item for item in result)
