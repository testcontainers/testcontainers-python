#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import annotations

import asyncio
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from os import PathLike
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Tuple, Callable

import requests
import torch
import numpy as np
from docker.types.containers import DeviceRequest
from pydantic import BaseModel, Field, validator, root_validator

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


# ============================================================================
# Core Enums and Types
# ============================================================================

class DeviceType(str, Enum):
    """Device types supported by VLLM."""
    CUDA = "cuda"
    CPU = "cpu"
    TPU = "tpu"
    XPU = "xpu"
    ROCM = "rocm"


class ModelType(str, Enum):
    """Model types supported by VLLM."""
    DECODER_ONLY = "decoder_only"
    ENCODER_DECODER = "encoder_decoder"
    EMBEDDING = "embedding"
    POOLING = "pooling"


class AttentionBackend(str, Enum):
    """Attention backends supported by VLLM."""
    FLASH_ATTN = "flash_attn"
    XFORMERS = "xformers"
    ROCM_FLASH_ATTN = "rocm_flash_attn"
    TORCH_SDPA = "torch_sdpa"


class SchedulerType(str, Enum):
    """Scheduler types for request management."""
    FCFS = "fcfs"  # First Come First Served
    PRIORITY = "priority"


class BlockSpacePolicy(str, Enum):
    """Block space policies for memory management."""
    GUARDED = "guarded"
    GUARDED_MMAP = "guarded_mmap"


class KVSpacePolicy(str, Enum):
    """KV cache space policies."""
    EAGER = "eager"
    LAZY = "lazy"


class QuantizationMethod(str, Enum):
    """Quantization methods supported by VLLM."""
    AWQ = "awq"
    GPTQ = "gptq"
    SQUEEZELLM = "squeezellm"
    FP8 = "fp8"
    MIXED = "mixed"
    BITSANDBYTES = "bitsandbytes"
    AUTOROUND = "autoround"
    QUARK = "quark"
    TORCHAO = "torchao"


class LoadFormat(str, Enum):
    """Model loading formats."""
    AUTO = "auto"
    TORCH = "torch"
    SAFETENSORS = "safetensors"
    NPZ = "npz"
    DUMMY = "dummy"


class TokenizerMode(str, Enum):
    """Tokenizer modes."""
    AUTO = "auto"
    SLOW = "slow"
    FAST = "fast"


class PoolingType(str, Enum):
    """Pooling types for embedding models."""
    MEAN = "mean"
    MAX = "max"
    CLS = "cls"
    LAST = "last"


class SpeculativeMode(str, Enum):
    """Speculative decoding modes."""
    SMALL_MODEL = "small_model"
    DRAFT_MODEL = "draft_model"
    MEDUSA = "medusa"


# ============================================================================
# Configuration Models
# ============================================================================

class ModelConfig(BaseModel):
    """Model-specific configuration."""
    model: str = Field(..., description="Model name or path")
    tokenizer: Optional[str] = Field(None, description="Tokenizer name or path")
    tokenizer_mode: TokenizerMode = Field(TokenizerMode.AUTO, description="Tokenizer mode")
    trust_remote_code: bool = Field(False, description="Trust remote code")
    download_dir: Optional[str] = Field(None, description="Download directory")
    load_format: LoadFormat = Field(LoadFormat.AUTO, description="Model loading format")
    dtype: str = Field("auto", description="Data type")
    seed: int = Field(0, description="Random seed")
    revision: Optional[str] = Field(None, description="Model revision")
    code_revision: Optional[str] = Field(None, description="Code revision")
    max_model_len: Optional[int] = Field(None, description="Maximum model length")
    quantization: Optional[QuantizationMethod] = Field(None, description="Quantization method")
    enforce_eager: bool = Field(False, description="Enforce eager execution")
    max_seq_len_to_capture: int = Field(8192, description="Max sequence length to capture")
    disable_custom_all_reduce: bool = Field(False, description="Disable custom all-reduce")
    skip_tokenizer_init: bool = Field(False, description="Skip tokenizer initialization")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "microsoft/DialoGPT-medium",
                "tokenizer_mode": "auto",
                "trust_remote_code": False,
                "load_format": "auto",
                "dtype": "auto"
            }
        }


class CacheConfig(BaseModel):
    """KV cache configuration."""
    block_size: int = Field(16, description="Block size for KV cache")
    gpu_memory_utilization: float = Field(0.9, description="GPU memory utilization")
    swap_space: int = Field(4, description="Swap space in GB")
    cache_dtype: str = Field("auto", description="Cache data type")
    num_gpu_blocks_override: Optional[int] = Field(None, description="Override number of GPU blocks")
    num_cpu_blocks_override: Optional[int] = Field(None, description="Override number of CPU blocks")
    block_space_policy: BlockSpacePolicy = Field(BlockSpacePolicy.GUARDED, description="Block space policy")
    kv_space_policy: KVSpacePolicy = Field(KVSpacePolicy.EAGER, description="KV space policy")
    enable_prefix_caching: bool = Field(False, description="Enable prefix caching")
    enable_chunked_prefill: bool = Field(False, description="Enable chunked prefill")
    preemption_mode: str = Field("recompute", description="Preemption mode")
    enable_hybrid_engine: bool = Field(False, description="Enable hybrid engine")
    num_lookahead_slots: int = Field(0, description="Number of lookahead slots")
    delay_factor: float = Field(0.0, description="Delay factor")
    enable_sliding_window: bool = Field(False, description="Enable sliding window")
    sliding_window_size: Optional[int] = Field(None, description="Sliding window size")
    sliding_window_blocks: Optional[int] = Field(None, description="Sliding window blocks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "block_size": 16,
                "gpu_memory_utilization": 0.9,
                "swap_space": 4,
                "cache_dtype": "auto"
            }
        }


class LoadConfig(BaseModel):
    """Model loading configuration."""
    max_model_len: Optional[int] = Field(None, description="Maximum model length")
    max_num_batched_tokens: Optional[int] = Field(None, description="Maximum batched tokens")
    max_num_seqs: Optional[int] = Field(None, description="Maximum number of sequences")
    max_paddings: Optional[int] = Field(None, description="Maximum paddings")
    max_lora_rank: int = Field(16, description="Maximum LoRA rank")
    max_loras: int = Field(1, description="Maximum number of LoRAs")
    max_cpu_loras: int = Field(2, description="Maximum CPU LoRAs")
    lora_extra_vocab_size: int = Field(256, description="LoRA extra vocabulary size")
    lora_dtype: str = Field("auto", description="LoRA data type")
    device_map: Optional[str] = Field(None, description="Device map")
    load_in_low_bit: Optional[str] = Field(None, description="Load in low bit")
    load_in_4bit: bool = Field(False, description="Load in 4-bit")
    load_in_8bit: bool = Field(False, description="Load in 8-bit")
    load_in_symmetric: bool = Field(True, description="Load in symmetric")
    load_in_nested: bool = Field(False, description="Load in nested")
    load_in_half: bool = Field(False, description="Load in half precision")
    load_in_bfloat16: bool = Field(False, description="Load in bfloat16")
    load_in_float16: bool = Field(False, description="Load in float16")
    load_in_float32: bool = Field(False, description="Load in float32")
    load_in_int8: bool = Field(False, description="Load in int8")
    load_in_int4: bool = Field(False, description="Load in int4")
    load_in_int2: bool = Field(False, description="Load in int2")
    load_in_int1: bool = Field(False, description="Load in int1")
    load_in_bool: bool = Field(False, description="Load in bool")
    load_in_uint8: bool = Field(False, description="Load in uint8")
    load_in_uint4: bool = Field(False, description="Load in uint4")
    load_in_uint2: bool = Field(False, description="Load in uint2")
    load_in_uint1: bool = Field(False, description="Load in uint1")
    load_in_complex64: bool = Field(False, description="Load in complex64")
    load_in_complex128: bool = Field(False, description="Load in complex128")
    load_in_quint8: bool = Field(False, description="Load in quint8")
    load_in_quint4x2: bool = Field(False, description="Load in quint4x2")
    load_in_quint2x4: bool = Field(False, description="Load in quint2x4")
    load_in_quint1x8: bool = Field(False, description="Load in quint1x8")
    load_in_qint8: bool = Field(False, description="Load in qint8")
    load_in_qint4: bool = Field(False, description="Load in qint4")
    load_in_qint2: bool = Field(False, description="Load in qint2")
    load_in_qint1: bool = Field(False, description="Load in qint1")
    load_in_bfloat8: bool = Field(False, description="Load in bfloat8")
    load_in_float8: bool = Field(False, description="Load in float8")
    load_in_half_bfloat16: bool = Field(False, description="Load in half bfloat16")
    load_in_half_float16: bool = Field(False, description="Load in half float16")
    load_in_half_float32: bool = Field(False, description="Load in half float32")
    load_in_half_int8: bool = Field(False, description="Load in half int8")
    load_in_half_int4: bool = Field(False, description="Load in half int4")
    load_in_half_int2: bool = Field(False, description="Load in half int2")
    load_in_half_int1: bool = Field(False, description="Load in half int1")
    load_in_half_bool: bool = Field(False, description="Load in half bool")
    load_in_half_uint8: bool = Field(False, description="Load in half uint8")
    load_in_half_uint4: bool = Field(False, description="Load in half uint4")
    load_in_half_uint2: bool = Field(False, description="Load in half uint2")
    load_in_half_uint1: bool = Field(False, description="Load in half uint1")
    load_in_half_complex64: bool = Field(False, description="Load in half complex64")
    load_in_half_complex128: bool = Field(False, description="Load in half complex128")
    load_in_half_quint8: bool = Field(False, description="Load in half quint8")
    load_in_half_quint4x2: bool = Field(False, description="Load in half quint4x2")
    load_in_half_quint2x4: bool = Field(False, description="Load in half quint2x4")
    load_in_half_quint1x8: bool = Field(False, description="Load in half quint1x8")
    load_in_half_qint8: bool = Field(False, description="Load in half qint8")
    load_in_half_qint4: bool = Field(False, description="Load in half qint4")
    load_in_half_qint2: bool = Field(False, description="Load in half qint2")
    load_in_half_qint1: bool = Field(False, description="Load in half qint1")
    load_in_half_bfloat8: bool = Field(False, description="Load in half bfloat8")
    load_in_half_float8: bool = Field(False, description="Load in half float8")
    
    class Config:
        json_schema_extra = {
            "example": {
                "max_model_len": 4096,
                "max_num_batched_tokens": 8192,
                "max_num_seqs": 256
            }
        }


class ParallelConfig(BaseModel):
    """Parallel execution configuration."""
    pipeline_parallel_size: int = Field(1, description="Pipeline parallel size")
    tensor_parallel_size: int = Field(1, description="Tensor parallel size")
    worker_use_ray: bool = Field(False, description="Use Ray for workers")
    engine_use_ray: bool = Field(False, description="Use Ray for engine")
    disable_custom_all_reduce: bool = Field(False, description="Disable custom all-reduce")
    max_parallel_loading_workers: Optional[int] = Field(None, description="Max parallel loading workers")
    ray_address: Optional[str] = Field(None, description="Ray cluster address")
    placement_group: Optional[Dict[str, Any]] = Field(None, description="Ray placement group")
    ray_runtime_env: Optional[Dict[str, Any]] = Field(None, description="Ray runtime environment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pipeline_parallel_size": 1,
                "tensor_parallel_size": 1,
                "worker_use_ray": False
            }
        }


class SchedulerConfig(BaseModel):
    """Scheduler configuration."""
    max_num_batched_tokens: int = Field(8192, description="Maximum batched tokens")
    max_num_seqs: int = Field(256, description="Maximum number of sequences")
    max_paddings: int = Field(256, description="Maximum paddings")
    use_v2_block_manager: bool = Field(False, description="Use v2 block manager")
    enable_chunked_prefill: bool = Field(False, description="Enable chunked prefill")
    preemption_mode: str = Field("recompute", description="Preemption mode")
    num_lookahead_slots: int = Field(0, description="Number of lookahead slots")
    delay_factor: float = Field(0.0, description="Delay factor")
    enable_sliding_window: bool = Field(False, description="Enable sliding window")
    sliding_window_size: Optional[int] = Field(None, description="Sliding window size")
    sliding_window_blocks: Optional[int] = Field(None, description="Sliding window blocks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "max_num_batched_tokens": 8192,
                "max_num_seqs": 256,
                "max_paddings": 256
            }
        }


class DeviceConfig(BaseModel):
    """Device configuration."""
    device: DeviceType = Field(DeviceType.CUDA, description="Device type")
    device_id: int = Field(0, description="Device ID")
    memory_fraction: float = Field(1.0, description="Memory fraction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device": "cuda",
                "device_id": 0,
                "memory_fraction": 1.0
            }
        }


class ObservabilityConfig(BaseModel):
    """Observability configuration."""
    disable_log_stats: bool = Field(False, description="Disable log statistics")
    disable_log_requests: bool = Field(False, description="Disable log requests")
    log_requests: bool = Field(False, description="Log requests")
    log_stats: bool = Field(False, description="Log statistics")
    log_level: str = Field("INFO", description="Log level")
    log_file: Optional[str] = Field(None, description="Log file")
    log_format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "disable_log_stats": False,
                "disable_log_requests": False,
                "log_level": "INFO"
            }
        }


class VllmConfig(BaseModel):
    """Complete VLLM configuration aggregating all components."""
    model: ModelConfig = Field(..., description="Model configuration")
    cache: CacheConfig = Field(..., description="Cache configuration")
    load: LoadConfig = Field(..., description="Load configuration")
    parallel: ParallelConfig = Field(..., description="Parallel configuration")
    scheduler: SchedulerConfig = Field(..., description="Scheduler configuration")
    device: DeviceConfig = Field(..., description="Device configuration")
    observability: ObservabilityConfig = Field(..., description="Observability configuration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": {
                    "model": "microsoft/DialoGPT-medium",
                    "tokenizer_mode": "auto"
                },
                "cache": {
                    "block_size": 16,
                    "gpu_memory_utilization": 0.9
                },
                "load": {
                    "max_model_len": 4096
                },
                "parallel": {
                    "pipeline_parallel_size": 1,
                    "tensor_parallel_size": 1
                },
                "scheduler": {
                    "max_num_batched_tokens": 8192,
                    "max_num_seqs": 256
                },
                "device": {
                    "device": "cuda",
                    "device_id": 0
                },
                "observability": {
                    "disable_log_stats": False,
                    "log_level": "INFO"
                }
            }
        }


class SamplingParams(BaseModel):
    """Sampling parameters for text generation."""
    n: int = Field(1, description="Number of output sequences to generate")
    best_of: Optional[int] = Field(None, description="Number of sequences to generate and return the best")
    presence_penalty: float = Field(0.0, description="Presence penalty")
    frequency_penalty: float = Field(0.0, description="Frequency penalty")
    repetition_penalty: float = Field(1.0, description="Repetition penalty")
    temperature: float = Field(1.0, description="Sampling temperature")
    top_p: float = Field(1.0, description="Top-p sampling parameter")
    top_k: int = Field(-1, description="Top-k sampling parameter")
    min_p: float = Field(0.0, description="Minimum probability threshold")
    use_beam_search: bool = Field(False, description="Use beam search")
    length_penalty: float = Field(1.0, description="Length penalty for beam search")
    early_stopping: Union[bool, str] = Field(False, description="Early stopping for beam search")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    stop_token_ids: Optional[List[int]] = Field(None, description="Stop token IDs")
    include_stop_str_in_output: bool = Field(False, description="Include stop string in output")
    ignore_eos: bool = Field(False, description="Ignore end-of-sequence token")
    skip_special_tokens: bool = Field(True, description="Skip special tokens in output")
    spaces_between_special_tokens: bool = Field(True, description="Add spaces between special tokens")
    logits_processor: Optional[List[Callable]] = Field(None, description="Logits processors")
    prompt_logprobs: Optional[int] = Field(None, description="Number of logprobs for prompt tokens")
    detokenize: bool = Field(True, description="Detokenize output")
    seed: Optional[int] = Field(None, description="Random seed")
    logprobs: Optional[int] = Field(None, description="Number of logprobs to return")
    
    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 50,
                "stop": ["\n", "Human:"]
            }
        }


# ============================================================================
# VLLM Integration Models
# ============================================================================

class VLLMServerConfig(BaseModel):
    """Configuration for VLLM server deployment."""
    model_name: str = Field(..., description="Model name or path")
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8000, description="Server port")
    gpu_memory_utilization: float = Field(0.9, description="GPU memory utilization")
    max_model_len: int = Field(4096, description="Maximum model length")
    dtype: str = Field("auto", description="Data type for model")
    trust_remote_code: bool = Field(False, description="Trust remote code")
    download_dir: Optional[str] = Field(None, description="Download directory for models")
    load_format: str = Field("auto", description="Model loading format")
    tensor_parallel_size: int = Field(1, description="Tensor parallel size")
    pipeline_parallel_size: int = Field(1, description="Pipeline parallel size")
    max_num_seqs: int = Field(256, description="Maximum number of sequences")
    max_num_batched_tokens: int = Field(8192, description="Maximum batched tokens")
    max_paddings: int = Field(256, description="Maximum paddings")
    disable_log_stats: bool = Field(False, description="Disable log statistics")
    revision: Optional[str] = Field(None, description="Model revision")
    code_revision: Optional[str] = Field(None, description="Code revision")
    tokenizer: Optional[str] = Field(None, description="Tokenizer name")
    tokenizer_mode: str = Field("auto", description="Tokenizer mode")
    skip_tokenizer_init: bool = Field(False, description="Skip tokenizer initialization")
    enforce_eager: bool = Field(False, description="Enforce eager execution")
    max_seq_len_to_capture: int = Field(8192, description="Max sequence length to capture")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "microsoft/DialoGPT-medium",
                "host": "0.0.0.0",
                "port": 8000,
                "gpu_memory_utilization": 0.9,
                "max_model_len": 4096
            }
        }


class VLLMEmbeddingServerConfig(BaseModel):
    """Configuration for VLLM embedding server deployment."""
    model_name: str = Field(..., description="Embedding model name or path")
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8001, description="Server port")
    gpu_memory_utilization: float = Field(0.9, description="GPU memory utilization")
    max_model_len: int = Field(512, description="Maximum model length for embeddings")
    dtype: str = Field("auto", description="Data type for model")
    trust_remote_code: bool = Field(False, description="Trust remote code")
    download_dir: Optional[str] = Field(None, description="Download directory for models")
    load_format: str = Field("auto", description="Model loading format")
    tensor_parallel_size: int = Field(1, description="Tensor parallel size")
    pipeline_parallel_size: int = Field(1, description="Pipeline parallel size")
    max_num_seqs: int = Field(256, description="Maximum number of sequences")
    max_num_batched_tokens: int = Field(8192, description="Maximum batched tokens")
    max_paddings: int = Field(256, description="Maximum paddings")
    disable_log_stats: bool = Field(False, description="Disable log statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "host": "0.0.0.0",
                "port": 8001,
                "gpu_memory_utilization": 0.9,
                "max_model_len": 512
            }
        }


# ============================================================================
# Utility Functions
# ============================================================================

def create_vllm_config(
    model: str,
    gpu_memory_utilization: float = 0.9,
    max_model_len: Optional[int] = None,
    dtype: str = "auto",
    trust_remote_code: bool = False,
    **kwargs
) -> VllmConfig:
    """Create a VLLM configuration with common defaults."""
    model_config = ModelConfig(
        model=model,
        trust_remote_code=trust_remote_code,
        dtype=dtype,
        max_model_len=max_model_len
    )
    
    cache_config = CacheConfig(
        gpu_memory_utilization=gpu_memory_utilization
    )
    
    load_config = LoadConfig(
        max_model_len=max_model_len
    )
    
    parallel_config = ParallelConfig()
    scheduler_config = SchedulerConfig()
    device_config = DeviceConfig()
    observability_config = ObservabilityConfig()
    
    return VllmConfig(
        model=model_config,
        cache=cache_config,
        load=load_config,
        parallel=parallel_config,
        scheduler=scheduler_config,
        device=device_config,
        observability=observability_config,
        **kwargs
    )


def create_sampling_params(
    temperature: float = 1.0,
    top_p: float = 1.0,
    top_k: int = -1,
    max_tokens: int = 16,
    stop: Optional[Union[str, List[str]]] = None,
    **kwargs
) -> SamplingParams:
    """Create sampling parameters with common defaults."""
    return SamplingParams(
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        stop=stop,
        **kwargs
    )


class VLLMModelInfo:
    """Information about a VLLM model."""
    
    def __init__(self, name: str, size: int = 0, status: str = "unknown"):
        self.name = name
        self.size = size
        self.status = status


class VLLMContainer(DockerContainer):
    """
    VLLM Container for high-performance LLM inference.

    :param image: the vllm image to use (default: :code:`vllm/vllm-openai:latest`)
    :param model_name: the model to load (default: :code:`microsoft/DialoGPT-medium`)
    :param host: server host (default: :code:`0.0.0.0`)
    :param port: server port (default: :code:`8000`)
    :param gpu_memory_utilization: GPU memory utilization (default: :code:`0.9`)
    :param max_model_len: maximum model length (default: :code:`4096`)
    :param tensor_parallel_size: tensor parallel size (default: :code:`1`)
    :param pipeline_parallel_size: pipeline parallel size (default: :code:`1`)
    :param trust_remote_code: trust remote code (default: :code:`False`)
    :param download_dir: directory to download models (default: :code:`None`)
    :param vllm_home: the directory to mount for model data (default: :code:`None`)

    Examples:

        .. doctest::

            >>> from testcontainers.vllm import VLLMContainer
            >>> with VLLMContainer(model_name="gpt2") as vllm:
            ...     vllm.get_health_status()
            {'status': 'healthy'}

        .. code-block:: python

            >>> import requests
            >>> from testcontainers.vllm import VLLMContainer
            >>> 
            >>> with VLLMContainer(model_name="microsoft/DialoGPT-medium") as vllm:
            ...     # Generate text
            ...     response = requests.post(
            ...         f"{vllm.get_api_url()}/v1/chat/completions",
            ...         json={
            ...             "model": "microsoft/DialoGPT-medium",
            ...             "messages": [{"role": "user", "content": "Hello, how are you?"}],
            ...             "max_tokens": 50,
            ...             "temperature": 0.7
            ...         }
            ...     )
            ...     result = response.json()
            ...     print(result["choices"][0]["message"]["content"])
    """

    VLLM_PORT = 8000

    def __init__(
        self,
        image: str = "vllm/vllm-openai:latest",
        model_name: str = "microsoft/DialoGPT-medium",
        host: str = "0.0.0.0",
        port: int = 8000,
        gpu_memory_utilization: float = 0.9,
        max_model_len: int = 4096,
        tensor_parallel_size: int = 1,
        pipeline_parallel_size: int = 1,
        trust_remote_code: bool = False,
        download_dir: Optional[Union[str, PathLike]] = None,
        vllm_home: Optional[Union[str, PathLike]] = None,
        **kwargs,
    ):
        super().__init__(image=image, **kwargs)
        
        # Store configuration
        self.model_name = model_name
        self.host = host
        self.port = port
        self.gpu_memory_utilization = gpu_memory_utilization
        self.max_model_len = max_model_len
        self.tensor_parallel_size = tensor_parallel_size
        self.pipeline_parallel_size = pipeline_parallel_size
        self.trust_remote_code = trust_remote_code
        self.download_dir = download_dir
        self.vllm_home = vllm_home
        
        # Expose the VLLM port
        self.with_exposed_ports(VLLMContainer.VLLM_PORT)
        
        # Add GPU capabilities if available
        self._check_and_add_gpu_capabilities()
        
        # Set up volume mappings
        self._setup_volume_mappings()

    def _check_and_add_gpu_capabilities(self):
        """Check for GPU capabilities and add them if available."""
        try:
            info = self.get_docker_client().client.info()
            if "nvidia" in info.get("Runtimes", {}):
                self._kwargs = {
                    **self._kwargs,
                    "device_requests": [DeviceRequest(count=-1, capabilities=[["gpu"]])]
                }
        except Exception:
            # If we can't detect GPU capabilities, continue without them
            pass

    def _setup_volume_mappings(self):
        """Set up volume mappings for model storage."""
        if self.vllm_home:
            self.with_volume_mapping(self.vllm_home, "/root/.cache/huggingface", "rw")
        
        if self.download_dir:
            self.with_volume_mapping(self.download_dir, "/models", "rw")

    def _build_vllm_command(self) -> List[str]:
        """Build the VLLM server command."""
        cmd = [
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", self.model_name,
            "--host", self.host,
            "--port", str(self.port),
            "--gpu-memory-utilization", str(self.gpu_memory_utilization),
            "--max-model-len", str(self.max_model_len),
            "--tensor-parallel-size", str(self.tensor_parallel_size),
            "--pipeline-parallel-size", str(self.pipeline_parallel_size),
        ]
        
        if self.trust_remote_code:
            cmd.append("--trust-remote-code")
        
        if self.download_dir:
            cmd.extend(["--download-dir", "/models"])
        
        return cmd

    def start(self) -> "VLLMContainer":
        """
        Start the VLLM server.
        """
        # Set the command to start VLLM server
        cmd = self._build_vllm_command()
        self.with_command(cmd)
        
        # Start the container
        super().start()
        
        # Wait for the server to be ready
        wait_for_logs(self, "Uvicorn running on", timeout=120)
        
        # Additional health check
        self._wait_for_health_check()
        
        return self

    def _wait_for_health_check(self, timeout: int = 60):
        """Wait for the VLLM server to be healthy."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.get_api_url()}/health", timeout=5)
                if response.status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(2)
        
        raise RuntimeError(f"VLLM server did not become healthy within {timeout} seconds")

    def get_api_url(self) -> str:
        """
        Return the API URL of the VLLM server.
        """
        host = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(VLLMContainer.VLLM_PORT)
        return f"http://{host}:{exposed_port}"

    def get_endpoint(self) -> str:
        """
        Return the endpoint of the VLLM server (alias for get_api_url).
        """
        return self.get_api_url()

    @property
    def id(self) -> str:
        """
        Return the container ID.
        """
        return self._container.id

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of the VLLM server.
        """
        try:
            response = requests.get(f"{self.get_api_url()}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.
        """
        try:
            response = requests.get(f"{self.get_api_url()}/v1/models", timeout=10)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to list models: {e}")

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 50,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> str:
        """
        Generate text using the VLLM server.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.get_api_url()}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to generate text: {e}")

    def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        model: Optional[str] = None
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings using the VLLM server.
        
        Args:
            texts: Text or list of texts to embed
            model: Model to use for embeddings (defaults to self.model_name)
            
        Returns:
            Embeddings as list of floats or list of lists of floats
        """
        if model is None:
            model = self.model_name
            
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False
        
        payload = {
            "model": model,
            "input": texts,
            "encoding_format": "float"
        }
        
        try:
            response = requests.post(
                f"{self.get_api_url()}/v1/embeddings",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            embeddings = [item["embedding"] for item in result["data"]]
            
            if single_text:
                return embeddings[0]
            return embeddings
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to generate embeddings: {e}")

    def get_vllm_config(self) -> VllmConfig:
        """
        Get the VLLM configuration used by this container.
        """
        return create_vllm_config(
            model=self.model_name,
            gpu_memory_utilization=self.gpu_memory_utilization,
            max_model_len=self.max_model_len,
            trust_remote_code=self.trust_remote_code
        )

    def get_server_config(self) -> VLLMServerConfig:
        """
        Get the VLLM server configuration.
        """
        return VLLMServerConfig(
            model_name=self.model_name,
            host=self.host,
            port=self.port,
            gpu_memory_utilization=self.gpu_memory_utilization,
            max_model_len=self.max_model_len,
            tensor_parallel_size=self.tensor_parallel_size,
            pipeline_parallel_size=self.pipeline_parallel_size,
            trust_remote_code=self.trust_remote_code,
            download_dir=str(self.download_dir) if self.download_dir else None
        )

    def commit_to_image(self, image_name: str) -> None:
        """
        Commit the current container to a new image.

        Args:
            image_name: Name of the new image
        """
        docker_client = self.get_docker_client()
        existing_images = docker_client.client.images.list(name=image_name)
        if not existing_images and self.id:
            docker_client.client.containers.get(self.id).commit(
                repository=image_name,
                conf={"Labels": {"org.testcontainers.session-id": ""}}
            )

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get server metrics.
        """
        try:
            response = requests.get(f"{self.get_api_url()}/metrics", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get metrics: {e}")

    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information.
        """
        try:
            response = requests.get(f"{self.get_api_url()}/v1/models", timeout=10)
            response.raise_for_status()
            models_data = response.json()
            
            health = self.get_health_status()
            
            return {
                "health": health,
                "models": models_data,
                "api_url": self.get_api_url(),
                "model_name": self.model_name,
                "config": {
                    "model_name": self.model_name,
                    "host": self.host,
                    "port": self.port,
                    "gpu_memory_utilization": self.gpu_memory_utilization,
                    "max_model_len": self.max_model_len,
                    "tensor_parallel_size": self.tensor_parallel_size,
                    "pipeline_parallel_size": self.pipeline_parallel_size,
                    "trust_remote_code": self.trust_remote_code,
                    "download_dir": str(self.download_dir) if self.download_dir else None
                }
            }
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get server info: {e}")