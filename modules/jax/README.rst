# Testcontainers : JAX

## Docker Containers for JAX with GPU Support

1. **Official JAX Docker Container**
   - **Container**: `jax/jax:cuda-12.0`
   - **Documentation**: [JAX Docker](https://github.com/google/jax/blob/main/docker/README.md)
   
2. **NVIDIA Docker Container**
   - **Container**: `nvidia/cuda:12.0-cudnn8-devel-ubuntu20.04`
   - **Documentation**: [NVIDIA Docker Hub](https://hub.docker.com/r/nvidia/cuda)

## Benefits of Having This Container

1. **Optimized Performance**: JAX uses XLA to compile and run NumPy programs on GPUs, which can significantly speed up numerical computations and machine learning tasks. A container specifically optimized for JAX with CUDA ensures that the environment is configured to leverage GPU acceleration fully.

2. **Reproducibility**: Containers encapsulate all dependencies, libraries, and configurations needed to run JAX, ensuring that the environment is consistent across different systems. This is crucial for reproducible research and development.

3. **Ease of Use**: Users can easily pull and run the container without worrying about the complex setup required for GPU support and JAX configuration. This reduces the barrier to entry for new users and accelerates development workflows.

4. **Isolation and Security**: Containers provide an isolated environment, which enhances security by limiting the impact of potential vulnerabilities. It also avoids conflicts with other software on the host system.

## Troubleshooting

**Ensure Docker is configured to use the NVIDIA runtime**:
   - You need to install the NVIDIA Container Toolkit. Follow the instructions for your operating system: [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).
   - Update your Docker daemon configuration to include the NVIDIA runtime. Edit the Docker daemon configuration file, typically located at `/etc/docker/daemon.json`, to include the following:
     
     ```json
     {
       "runtimes": {
         "nvidia": {
           "path": "nvidia-container-runtime",
           "runtimeArgs": []
         }
       }
     }
     ```

   - Restart the Docker daemon to apply the changes:
     ```sh
     sudo systemctl restart docker
     ```

## Relevant Reading Material

1. **JAX Documentation**
   - [JAX Quickstart](https://github.com/google/jax#quickstart)
   - [JAX Transformations](https://github.com/google/jax#transformations)
   - [JAX Installation Guide](https://github.com/google/jax#installation)

2. **NVIDIA Docker Documentation**
   - [NVIDIA Docker Hub](https://hub.docker.com/r/nvidia/cuda)
   - [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)

3. **Docker Best Practices**
   - [Docker Documentation](https://docs.docker.com/get-started/)
   - [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)