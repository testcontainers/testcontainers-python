import requests

from testcontainers.ollama import OllamaContainer


def basic_example():
    with OllamaContainer() as ollama:
        # Get API endpoint
        api_url = ollama.get_api_url()

        # Pull a model
        model_name = "llama2"
        print(f"Pulling model: {model_name}")
        response = requests.post(f"{api_url}/api/pull", json={"name": model_name})
        print(f"Pull response: {response.json()}")

        # Generate text
        prompt = "Write a short poem about programming."
        print(f"\nGenerating text for prompt: {prompt}")

        response = requests.post(
            f"{api_url}/api/generate", json={"model": model_name, "prompt": prompt, "stream": False}
        )

        result = response.json()
        print("\nGenerated text:")
        print(result["response"])

        # Embed text
        text_to_embed = "The quick brown fox jumps over the lazy dog"
        print(f"\nGenerating embedding for: {text_to_embed}")

        response = requests.post(f"{api_url}/api/embeddings", json={"model": model_name, "prompt": text_to_embed})

        embedding = response.json()
        print("\nEmbedding:")
        print(f"Length: {len(embedding['embedding'])}")
        print(f"First 5 values: {embedding['embedding'][:5]}")

        # List available models
        response = requests.get(f"{api_url}/api/tags")
        models = response.json()

        print("\nAvailable models:")
        for model in models["models"]:
            print(f"Name: {model['name']}, Size: {model['size']}")


if __name__ == "__main__":
    basic_example()
