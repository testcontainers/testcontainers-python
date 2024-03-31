.. autoclass:: testcontainers.registry.DockerRegistryContainer

When building Docker containers with Docker Buildx there is currently no option to test your containers locally without
a local registry. Otherwise Buildx pushes your image to Docker Hub, which is not what you want in a test case. More
and more you need to use Buildx for efficiently building images and especially multi arch images.

When you use Docker Python libraries like docker-py or python-on-whales to build and test Docker images, what a lot of
persons and DevOps engineers like me nowadays do, a test container comes in very handy.
