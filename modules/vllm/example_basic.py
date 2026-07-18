import requests
import json
from testcontainers.vllm import VLLMContainer


def basic_example():
    """Basic example of using VLLMContainer for text generation and embeddings."""
    
    with VLLMContainer(
        model_name="microsoft/DialoGPT-medium",
        gpu_memory_utilization=0.8,
        max_model_len=1024
    ) as vllm:
        # Get API endpoint
        api_url = vllm.get_api_url()
        print(f"VLLM API URL: {api_url}")

        # Check health status
        health = vllm.get_health_status()
        print(f"Health status: {health}")

        # List available models
        models = vllm.list_models()
        print(f"Available models: {json.dumps(models, indent=2)}")

        # Generate text using chat completions
        prompt = "Write a short poem about artificial intelligence."
        print(f"\nGenerating text for prompt: {prompt}")

        response = requests.post(
            f"{api_url}/v1/chat/completions",
            json={
                "model": "microsoft/DialoGPT-medium",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9
            }
        )

        result = response.json()
        print("\nGenerated text:")
        print(result["choices"][0]["message"]["content"])

        # Generate embeddings
        text_to_embed = "The quick brown fox jumps over the lazy dog"
        print(f"\nGenerating embedding for: {text_to_embed}")

        try:
            embedding = vllm.generate_embeddings(text_to_embed)
            print(f"\nEmbedding:")
            print(f"Length: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        except Exception as e:
            print(f"Embedding generation failed (model may not support embeddings): {e}")

        # Get server information
        server_info = vllm.get_server_info()
        print(f"\nServer info:")
        print(f"Model: {server_info['model_name']}")
        print(f"Health: {server_info['health']['status']}")


def advanced_example():
    """Advanced example with custom configuration and streaming."""
    
    with VLLMContainer(
        model_name="gpt2",
        gpu_memory_utilization=0.9,
        max_model_len=512,
        tensor_parallel_size=1,
        trust_remote_code=False
    ) as vllm:
        api_url = vllm.get_api_url()
        
        # Generate text with custom parameters
        prompt = "Once upon a time in a land far away"
        print(f"Generating text with custom parameters for: {prompt}")
        
        response = requests.post(
            f"{api_url}/v1/chat/completions",
            json={
                "model": "gpt2",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.8,
                "top_p": 0.95,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
        )
        
        result = response.json()
        print("Generated text:")
        print(result["choices"][0]["message"]["content"])
        
        # Test streaming (if supported)
        print("\nTesting streaming generation:")
        try:
            response = requests.post(
                f"{api_url}/v1/chat/completions",
                json={
                    "model": "gpt2",
                    "messages": [{"role": "user", "content": "Tell me a joke"}],
                    "max_tokens": 30,
                    "temperature": 0.7,
                    "stream": True
                },
                stream=True
            )
            
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    print(delta['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            continue
            print()  # New line after streaming
            
        except Exception as e:
            print(f"Streaming failed: {e}")


def configuration_example():
    """Example showing different configuration options."""
    
    # Example with custom download directory and model home
    with VLLMContainer(
        model_name="microsoft/DialoGPT-small",
        gpu_memory_utilization=0.7,
        max_model_len=2048,
        tensor_parallel_size=1,
        pipeline_parallel_size=1,
        trust_remote_code=True
    ) as vllm:
        # Get the VLLM configuration
        config = vllm.get_vllm_config()
        print("VLLM Configuration:")
        print(f"Model: {config.model.model}")
        print(f"GPU Memory Utilization: {config.cache.gpu_memory_utilization}")
        print(f"Max Model Length: {config.model.max_model_len}")
        print(f"Trust Remote Code: {config.model.trust_remote_code}")
        
        # Get server configuration
        server_config = vllm.get_server_config()
        print(f"\nServer Configuration:")
        print(f"Host: {server_config.host}")
        print(f"Port: {server_config.port}")
        print(f"Tensor Parallel Size: {server_config.tensor_parallel_size}")
        
        # Test basic functionality
        health = vllm.get_health_status()
        print(f"\nHealth Status: {health['status']}")


def batch_processing_example():
    """Example of batch processing multiple requests."""
    
    with VLLMContainer(model_name="gpt2") as vllm:
        api_url = vllm.get_api_url()
        
        # Prepare multiple prompts
        prompts = [
            "What is artificial intelligence?",
            "Explain machine learning in simple terms.",
            "What are the benefits of automation?"
        ]
        
        print("Processing batch of prompts:")
        
        # Process each prompt
        for i, prompt in enumerate(prompts, 1):
            print(f"\n{i}. {prompt}")
            
            response = requests.post(
                f"{api_url}/v1/chat/completions",
                json={
                    "model": "gpt2",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 50,
                    "temperature": 0.7
                }
            )
            
            result = response.json()
            print(f"Response: {result['choices'][0]['message']['content']}")


if __name__ == "__main__":
    print("=== Basic VLLM Container Example ===")
    basic_example()
    
    print("\n=== Advanced VLLM Container Example ===")
    advanced_example()
    
    print("\n=== Configuration Example ===")
    configuration_example()
    
    print("\n=== Batch Processing Example ===")
    batch_processing_example()
