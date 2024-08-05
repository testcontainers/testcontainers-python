import logging
import tempfile
import time
from typing import Optional

from core.testcontainers.core.container import DockerContainer
from core.testcontainers.core.waiting_utils import wait_container_is_ready
from urllib.error import URLError

class WhisperJAXContainer(DockerContainer):
    """
    Whisper-JAX container for fast speech recognition and transcription.

    Example:

        .. doctest::

            >>> from testcontainers.whisper_jax import WhisperJAXContainer

            >>> with WhisperJAXContainer("openai/whisper-large-v2") as whisper:
            ...     # Connect to the container
            ...     whisper.connect()
            ...     
            ...     # Transcribe an audio file
            ...     result = whisper.transcribe_file("path/to/audio/file.wav")
            ...     print(result['text'])
            ...
            ...     # Transcribe a YouTube video
            ...     result = whisper.transcribe_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            ...     print(result['text'])
    """

    def __init__(self, model_name: str = "openai/whisper-large-v2", **kwargs):
        super().__init__("nvcr.io/nvidia/jax:23.08-py3", **kwargs)
        self.model_name = model_name
        self.with_exposed_ports(8888)  # Expose Jupyter notebook port
        self.with_env("NVIDIA_VISIBLE_DEVICES", "all")
        self.with_env("CUDA_VISIBLE_DEVICES", "all")
        self.with_kwargs(runtime="nvidia")  # Use NVIDIA runtime for GPU support

        # Install required dependencies
        self.with_command("sh -c '"
                          "pip install --no-cache-dir git+https://github.com/sanchit-gandhi/whisper-jax.git && "
                          "pip install --no-cache-dir numpy soundfile youtube_dl transformers datasets && "
                          "python -m pip install --upgrade --no-cache-dir jax jaxlib -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html && "
                          "jupyter notebook --ip 0.0.0.0 --port 8888 --allow-root --NotebookApp.token='' --NotebookApp.password=''"
                          "'")

    @wait_container_is_ready(URLError)
    def _connect(self):
        url = f"http://{self.get_container_host_ip()}:{self.get_exposed_port(8888)}"
        res = urllib.request.urlopen(url)
        if res.status != 200:
            raise Exception(f"Failed to connect to Whisper-JAX container. Status: {res.status}")

    def connect(self):
        """
        Connect to the Whisper-JAX container and ensure it's ready.
        """
        self._connect()
        logging.info("Successfully connected to Whisper-JAX container")

    def run_command(self, command: str):
        """
        Run a Python command inside the container.
        """
        exec_result = self.exec(f"python -c '{command}'")
        return exec_result

    def transcribe_file(self, file_path: str, task: str = "transcribe", return_timestamps: bool = False):
        """
        Transcribe an audio file using Whisper-JAX.
        """
        command = f"""
import soundfile as sf
from whisper_jax import FlaxWhisperPipline
import jax.numpy as jnp

pipeline = FlaxWhisperPipline("{self.model_name}", dtype=jnp.bfloat16, batch_size=16)
audio, sr = sf.read("{file_path}")
result = pipeline({{"array": audio, "sampling_rate": sr}}, task="{task}", return_timestamps={return_timestamps})
print(result)
"""
        return self.run_command(command)

    def transcribe_youtube(self, youtube_url: str, task: str = "transcribe", return_timestamps: bool = False):
        """
        Transcribe a YouTube video using Whisper-JAX.
        """
        command = f"""
import tempfile
import youtube_dl
import soundfile as sf
from whisper_jax import FlaxWhisperPipline
import jax.numpy as jnp

def download_youtube_audio(youtube_url, output_file):
    ydl_opts = {{
        'format': 'bestaudio/best',
        'postprocessors': [{{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }}],
        'outtmpl': output_file,
    }}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

pipeline = FlaxWhisperPipline("{self.model_name}", dtype=jnp.bfloat16, batch_size=16)

with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
    download_youtube_audio("{youtube_url}", temp_file.name)
    audio, sr = sf.read(temp_file.name)
    result = pipeline({{"array": audio, "sampling_rate": sr}}, task="{task}", return_timestamps={return_timestamps})
    print(result)
"""
        return self.run_command(command)

    def start(self):
        """
        Start the Whisper-JAX container.
        """
        super().start()
        logging.info(f"Whisper-JAX container started. Jupyter URL: http://{self.get_container_host_ip()}:{self.get_exposed_port(8888)}")
        return self
