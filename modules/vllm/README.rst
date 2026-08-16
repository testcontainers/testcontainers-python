.. autoclass:: testcontainers.vllm.VLLMContainer
.. title:: testcontainers.vllm.VLLMContainer

VLLM Container
==============

The VLLMContainer provides a high-performance LLM inference server using the VLLM framework. It supports various models, GPU acceleration, and OpenAI-compatible API endpoints.

Features
--------

- **High Performance**: Optimized for fast LLM inference with VLLM
- **GPU Support**: Automatic GPU detection and configuration
- **OpenAI Compatible**: Full OpenAI API compatibility for easy integration
- **Model Flexibility**: Support for various model formats and sizes
- **Embedding Support**: Generate embeddings for text
- **Streaming**: Support for streaming text generation
- **Batch Processing**: Efficient batch processing capabilities

Basic Usage
-----------

.. code-block:: python

    from testcontainers.vllm import VLLMContainer
    import requests

    with VLLMContainer(model_name="microsoft/DialoGPT-medium") as vllm:
        # Generate text
        response = requests.post(
            f"{vllm.get_api_url()}/v1/chat/completions",
            json={
                "model": "microsoft/DialoGPT-medium",
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "max_tokens": 50,
                "temperature": 0.7
            }
        )
        
        result = response.json()
        print(result["choices"][0]["message"]["content"])

Configuration Options
---------------------

The VLLMContainer supports various configuration options:

.. code-block:: python

    with VLLMContainer(
        model_name="gpt2",
        gpu_memory_utilization=0.9,
        max_model_len=2048,
        tensor_parallel_size=2,
        pipeline_parallel_size=1,
        trust_remote_code=True
    ) as vllm:
        # Your code here
        pass

Parameters
----------

- **image**: Docker image to use (default: ``vllm/vllm-openai:latest``)
- **model_name**: Model to load (default: ``microsoft/DialoGPT-medium``)
- **host**: Server host (default: ``0.0.0.0``)
- **port**: Server port (default: ``8000``)
- **gpu_memory_utilization**: GPU memory utilization (default: ``0.9``)
- **max_model_len**: Maximum model length (default: ``4096``)
- **tensor_parallel_size**: Tensor parallel size (default: ``1``)
- **pipeline_parallel_size**: Pipeline parallel size (default: ``1``)
- **trust_remote_code**: Trust remote code (default: ``False``)
- **download_dir**: Directory to download models (default: ``None``)
- **vllm_home**: Directory to mount for model data (default: ``None``)

API Methods
-----------

Health and Status
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Check health status
    health = vllm.get_health_status()
    
    # Get server information
    server_info = vllm.get_server_info()
    
    # List available models
    models = vllm.list_models()

Text Generation
~~~~~~~~~~~~~~~

.. code-block:: python

    # Generate text using the container method
    text = vllm.generate_text(
        prompt="Write a short story",
        max_tokens=100,
        temperature=0.7
    )
    
    # Or use direct API calls
    response = requests.post(
        f"{vllm.get_api_url()}/v1/chat/completions",
        json={
            "model": "microsoft/DialoGPT-medium",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 50
        }
    )

Embeddings
~~~~~~~~~~

.. code-block:: python

    # Generate embeddings
    embeddings = vllm.generate_embeddings("Hello, world!")
    
    # Batch embeddings
    texts = ["Hello", "World", "VLLM"]
    batch_embeddings = vllm.generate_embeddings(texts)

Streaming
~~~~~~~~~

.. code-block:: python

    import json

    response = requests.post(
        f"{vllm.get_api_url()}/v1/chat/completions",
        json={
            "model": "microsoft/DialoGPT-medium",
            "messages": [{"role": "user", "content": "Tell me a story"}],
            "max_tokens": 100,
            "stream": True
        },
        stream=True
    )

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
                            print(delta['content'], end='', flush=True)
                except json.JSONDecodeError:
                    continue

Advanced Configuration
----------------------

Using VLLM Configuration Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from testcontainers.vllm import VLLMContainer
    from dataclasses import create_vllm_config, SamplingParams

    with VLLMContainer(model_name="gpt2") as vllm:
        # Get VLLM configuration
        config = vllm.get_vllm_config()
        
        # Get server configuration
        server_config = vllm.get_server_config()
        
        # Use with sampling parameters
        sampling_params = SamplingParams(
            temperature=0.8,
            top_p=0.9,
            max_tokens=100
        )

GPU Support
-----------

The container automatically detects and configures GPU support when available:

.. code-block:: python

    # GPU support is automatically detected
    with VLLMContainer(
        model_name="microsoft/DialoGPT-medium",
        gpu_memory_utilization=0.9
    ) as vllm:
        # Container will use GPU if available
        pass

Model Persistence
-----------------

To persist models between container runs:

.. code-block:: python

    from pathlib import Path

    # Use a persistent directory for models
    model_dir = Path.home() / ".vllm_models"
    
    with VLLMContainer(
        model_name="microsoft/DialoGPT-medium",
        vllm_home=model_dir
    ) as vllm:
        # Models will be cached in model_dir
        pass

Error Handling
--------------

.. code-block:: python

    try:
        with VLLMContainer(model_name="invalid-model") as vllm:
            # This will fail if the model doesn't exist
            pass
    except Exception as e:
        print(f"Container failed to start: {e}")

Performance Tips
----------------

1. **GPU Memory**: Adjust `gpu_memory_utilization` based on your GPU memory
2. **Model Length**: Set appropriate `max_model_len` for your use case
3. **Parallel Processing**: Use `tensor_parallel_size` for multi-GPU setups
4. **Model Caching**: Use `vllm_home` to cache models between runs

Example Applications
--------------------

RAG System
~~~~~~~~~~

.. code-block:: python

    from testcontainers.vllm import VLLMContainer
    import requests

    with VLLMContainer(model_name="microsoft/DialoGPT-medium") as vllm:
        # Generate embeddings for documents
        documents = ["Document 1", "Document 2", "Document 3"]
        embeddings = vllm.generate_embeddings(documents)
        
        # Generate responses with context
        context = "Based on the documents: " + " ".join(documents)
        response = vllm.generate_text(
            prompt="Summarize the key points",
            context=context,
            max_tokens=100
        )

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

    with VLLMContainer(model_name="gpt2") as vllm:
        prompts = [
            "What is AI?",
            "Explain machine learning",
            "What is deep learning?"
        ]
        
        for prompt in prompts:
            response = vllm.generate_text(prompt, max_tokens=50)
            print(f"Q: {prompt}")
            print(f"A: {response}\n")

Integration with VLLM Dataclass
-------------------------------

The container integrates seamlessly with the VLLM dataclass system:

.. code-block:: python

    from testcontainers.vllm import VLLMContainer
    from dataclasses import VllmConfig, SamplingParams
    from integration import VLLMRAGSystem, VLLMDeployment

    # Create deployment configuration
    deployment = VLLMDeployment(
        llm_config=VLLMServerConfig(
            model_name="microsoft/DialoGPT-medium",
            port=8000
        )
    )
    
    # Use with container
    with VLLMContainer(model_name="microsoft/DialoGPT-medium") as vllm:
        # Get configuration objects
        config = vllm.get_vllm_config()
        server_config = vllm.get_server_config()
        
        # Use with RAG system
        rag_system = VLLMRAGSystem(deployment=deployment)
        # Initialize and use the RAG system
