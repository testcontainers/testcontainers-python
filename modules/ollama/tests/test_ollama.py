import random
import string
from pathlib import Path

import requests
from testcontainers.ollama import OllamaContainer


def random_string(length=6):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def test_ollama_container():
    with OllamaContainer() as ollama:
        url = ollama.get_endpoint()
        response = requests.get(url)
        assert response.status_code == 200
        assert response.text == "Ollama is running"


def test_with_default_config():
    with OllamaContainer("ollama/ollama:0.1.26") as ollama:
        ollama.start()
        response = requests.get(f"{ollama.get_endpoint()}/api/version")
        version = response.json().get("version")
        assert version == "0.1.26"


def test_download_model_and_commit_to_image():
    new_image_name = f"tc-ollama-allminilm-{random_string(length=4).lower()}"
    with OllamaContainer("ollama/ollama:0.1.26") as ollama:
        ollama.start()
        # Pull the model
        ollama.pull_model("all-minilm")

        response = requests.get(f"{ollama.get_endpoint()}/api/tags")
        model_name = ollama.list_models()[0].get("name")
        assert "all-minilm" in model_name

        # Commit the container state to a new image
        ollama.commit_to_image(new_image_name)

    # Verify the new image
    with OllamaContainer(new_image_name) as ollama:
        ollama.start()
        response = requests.get(f"{ollama.get_endpoint()}/api/tags")
        model_name = response.json().get("models", [])[0].get("name")
        assert "all-minilm" in model_name


def test_models_saved_in_folder(tmp_path: Path):
    with OllamaContainer("ollama/ollama:0.1.26", ollama_dir=tmp_path) as ollama:
        assert len(ollama.list_models()) == 0
        ollama.pull_model("all-minilm")
        assert len(ollama.list_models()) == 1
        assert "all-minilm" in ollama.list_models()[0].get("name")

    with OllamaContainer("ollama/ollama:0.1.26", ollama_dir=tmp_path) as ollama:
        assert len(ollama.list_models()) == 1
        assert "all-minilm" in ollama.list_models()[0].get("name")
