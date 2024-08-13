import pytest
from modules.jax.testcontainers.whisper_cuda.whisper_transcription import WhisperJAXContainer


@pytest.mark.parametrize("model_name", ["openai/whisper-tiny", "openai/whisper-base"])
def test_whisper_jax_container(model_name):
    with WhisperJAXContainer(model_name) as whisper:
        whisper.connect()

        # Test file transcription
        result = whisper.transcribe_file("/path/to/test/audio.wav")
        assert isinstance(result, dict)
        assert "text" in result
        assert isinstance(result["text"], str)

        # Test YouTube transcription
        result = whisper.transcribe_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert isinstance(result, dict)
        assert "text" in result
        assert isinstance(result["text"], str)


def test_whisper_jax_container_with_timestamps():
    with WhisperJAXContainer() as whisper:
        whisper.connect()

        result = whisper.transcribe_file("/path/to/test/audio.wav", return_timestamps=True)
        assert isinstance(result, dict)
        assert "text" in result
        assert "chunks" in result
        assert isinstance(result["chunks"], list)
        assert all("timestamp" in chunk for chunk in result["chunks"])
