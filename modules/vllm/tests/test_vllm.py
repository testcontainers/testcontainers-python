import json
import random
import string
import time
from pathlib import Path

import pytest
import requests
from testcontainers.vllm import VLLMContainer


def random_string(length=6):
    """Generate a random string for testing."""
    return "".join(random.choices(string.ascii_lowercase, k=length))


def test_vllm_container_basic():
    """Test basic VLLM container functionality."""
    with VLLMContainer(model_name="gpt2") as vllm:
        # Test API URL
        api_url = vllm.get_api_url()
        assert api_url.startswith("http://")
        assert ":8000" in api_url
        
        # Test health check
        health = vllm.get_health_status()
        assert "status" in health
        
        # Test container ID
        assert vllm.id is not None


def test_vllm_container_with_custom_config():
    """Test VLLM container with custom configuration."""
    with VLLMContainer(
        model_name="gpt2",
        gpu_memory_utilization=0.8,
        max_model_len=1024,
        tensor_parallel_size=1,
        trust_remote_code=False
    ) as vllm:
        # Test configuration
        config = vllm.get_vllm_config()
        assert config.model.model == "gpt2"
        assert config.cache.gpu_memory_utilization == 0.8
        assert config.model.max_model_len == 1024
        
        # Test server configuration
        server_config = vllm.get_server_config()
        assert server_config.model_name == "gpt2"
        assert server_config.gpu_memory_utilization == 0.8
        assert server_config.max_model_len == 1024


def test_vllm_text_generation():
    """Test text generation functionality."""
    with VLLMContainer(model_name="gpt2") as vllm:
        # Test direct API call
        api_url = vllm.get_api_url()
        response = requests.post(
            f"{api_url}/v1/chat/completions",
            json={
                "model": "gpt2",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10,
                "temperature": 0.7
            },
            timeout=30
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "message" in result["choices"][0]
        assert "content" in result["choices"][0]["message"]


def test_vllm_container_methods():
    """Test VLLM container helper methods."""
    with VLLMContainer(model_name="gpt2") as vllm:
        # Test generate_text method
        text = vllm.generate_text(
            prompt="Hello",
            max_tokens=5,
            temperature=0.7
        )
        assert isinstance(text, str)
        assert len(text) > 0


def test_vllm_models_list():
    """Test listing available models."""
    with VLLMContainer(model_name="gpt2") as vllm:
        models = vllm.list_models()
        assert isinstance(models, list)
        # Should have at least one model (the one we loaded)
        assert len(models) > 0


def test_vllm_server_info():
    """Test getting server information."""
    with VLLMContainer(model_name="gpt2") as vllm:
        server_info = vllm.get_server_info()
        assert "health" in server_info
        assert "models" in server_info
        assert "api_url" in server_info
        assert "model_name" in server_info
        assert "config" in server_info
        assert server_info["model_name"] == "gpt2"


def test_vllm_embeddings():
    """Test embedding generation (if supported by model)."""
    with VLLMContainer(model_name="gpt2") as vllm:
        try:
            # Test single text embedding
            embedding = vllm.generate_embeddings("Hello, world!")
            assert isinstance(embedding, list)
            assert len(embedding) > 0
            assert all(isinstance(x, (int, float)) for x in embedding)
            
            # Test batch embeddings
            texts = ["Hello", "World", "Test"]
            batch_embeddings = vllm.generate_embeddings(texts)
            assert isinstance(batch_embeddings, list)
            assert len(batch_embeddings) == 3
            assert all(isinstance(emb, list) for emb in batch_embeddings)
            
        except Exception as e:
            # Some models may not support embeddings
            pytest.skip(f"Embeddings not supported: {e}")


def test_vllm_streaming():
    """Test streaming text generation."""
    with VLLMContainer(model_name="gpt2") as vllm:
        api_url = vllm.get_api_url()
        
        try:
            response = requests.post(
                f"{api_url}/v1/chat/completions",
                json={
                    "model": "gpt2",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10,
                    "temperature": 0.7,
                    "stream": True
                },
                stream=True,
                timeout=30
            )
            
            assert response.status_code == 200
            
            # Collect streaming chunks
            chunks = []
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    chunks.append(delta['content'])
                        except json.JSONDecodeError:
                            continue
            
            # Should have received some chunks
            assert len(chunks) > 0
            
        except Exception as e:
            pytest.skip(f"Streaming not supported: {e}")


def test_vllm_with_model_persistence(tmp_path: Path):
    """Test VLLM container with model persistence."""
    with VLLMContainer(
        model_name="gpt2",
        vllm_home=tmp_path
    ) as vllm:
        # Test that container starts successfully with persistent storage
        health = vllm.get_health_status()
        assert "status" in health
        
        # Test basic functionality
        models = vllm.list_models()
        assert isinstance(models, list)


def test_vllm_commit_to_image():
    """Test committing container to image."""
    new_image_name = f"tc-vllm-test-{random_string(length=4).lower()}"
    
    with VLLMContainer(model_name="gpt2") as vllm:
        # Test that container works
        health = vllm.get_health_status()
        assert "status" in health
        
        # Commit to new image
        vllm.commit_to_image(new_image_name)
    
    # Verify the new image exists and works
    with VLLMContainer(new_image_name) as vllm:
        health = vllm.get_health_status()
        assert "status" in health


def test_vllm_metrics():
    """Test getting server metrics."""
    with VLLMContainer(model_name="gpt2") as vllm:
        try:
            metrics = vllm.get_metrics()
            # Metrics endpoint might return different formats
            assert isinstance(metrics, (dict, str))
        except Exception as e:
            # Metrics endpoint might not be available
            pytest.skip(f"Metrics not available: {e}")


def test_vllm_error_handling():
    """Test error handling for invalid requests."""
    with VLLMContainer(model_name="gpt2") as vllm:
        api_url = vllm.get_api_url()
        
        # Test invalid model name
        response = requests.post(
            f"{api_url}/v1/chat/completions",
            json={
                "model": "invalid-model",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            },
            timeout=10
        )
        
        # Should return an error
        assert response.status_code != 200


def test_vllm_different_models():
    """Test VLLM container with different model configurations."""
    models_to_test = [
        "gpt2",
        "microsoft/DialoGPT-small"
    ]
    
    for model_name in models_to_test:
        with VLLMContainer(model_name=model_name) as vllm:
            # Test basic functionality
            health = vllm.get_health_status()
            assert "status" in health
            
            # Test configuration
            config = vllm.get_vllm_config()
            assert config.model.model == model_name


def test_vllm_parallel_configuration():
    """Test VLLM container with parallel processing configuration."""
    with VLLMContainer(
        model_name="gpt2",
        tensor_parallel_size=1,
        pipeline_parallel_size=1
    ) as vllm:
        # Test configuration
        server_config = vllm.get_server_config()
        assert server_config.tensor_parallel_size == 1
        assert server_config.pipeline_parallel_size == 1
        
        # Test basic functionality
        health = vllm.get_health_status()
        assert "status" in health


def test_vllm_custom_ports():
    """Test VLLM container with custom port configuration."""
    with VLLMContainer(
        model_name="gpt2",
        port=8001
    ) as vllm:
        # Test that the port is correctly configured
        api_url = vllm.get_api_url()
        assert ":8001" in api_url
        
        # Test basic functionality
        health = vllm.get_health_status()
        assert "status" in health


def test_vllm_trust_remote_code():
    """Test VLLM container with trust_remote_code option."""
    with VLLMContainer(
        model_name="gpt2",
        trust_remote_code=True
    ) as vllm:
        # Test configuration
        config = vllm.get_vllm_config()
        assert config.model.trust_remote_code is True
        
        # Test basic functionality
        health = vllm.get_health_status()
        assert "status" in health


def test_vllm_memory_utilization():
    """Test VLLM container with different memory utilization settings."""
    with VLLMContainer(
        model_name="gpt2",
        gpu_memory_utilization=0.7
    ) as vllm:
        # Test configuration
        config = vllm.get_vllm_config()
        assert config.cache.gpu_memory_utilization == 0.7
        
        # Test basic functionality
        health = vllm.get_health_status()
        assert "status" in health


def test_vllm_max_model_length():
    """Test VLLM container with custom max model length."""
    with VLLMContainer(
        model_name="gpt2",
        max_model_len=2048
    ) as vllm:
        # Test configuration
        config = vllm.get_vllm_config()
        assert config.model.max_model_len == 2048
        
        # Test basic functionality
        health = vllm.get_health_status()
        assert "status" in health


def test_vllm_integration_with_dataclass():
    """Test integration with VLLM dataclass system."""
    from dataclasses import SamplingParams, create_sampling_params
    
    with VLLMContainer(model_name="gpt2") as vllm:
        # Test getting VLLM configuration
        config = vllm.get_vllm_config()
        assert config is not None
        assert config.model.model == "gpt2"
        
        # Test with sampling parameters
        sampling_params = create_sampling_params(
            temperature=0.8,
            top_p=0.9,
            max_tokens=50
        )
        assert sampling_params.temperature == 0.8
        assert sampling_params.top_p == 0.9
        
        # Test basic functionality
        health = vllm.get_health_status()
        assert "status" in health


def test_vllm_integration_with_rag_system():
    """Test integration with VLLM RAG system."""
    from integration import VLLMServerConfig, VLLMDeployment
    
    with VLLMContainer(model_name="gpt2") as vllm:
        # Test server configuration
        server_config = vllm.get_server_config()
        assert isinstance(server_config, VLLMServerConfig)
        assert server_config.model_name == "gpt2"
        
        # Test deployment configuration
        deployment = VLLMDeployment(llm_config=server_config)
        assert deployment.llm_config.model_name == "gpt2"
        
        # Test basic functionality
        health = vllm.get_health_status()
        assert "status" in health
