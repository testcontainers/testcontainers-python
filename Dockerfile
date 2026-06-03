ARG PYTHON_VERSION=3.10
# see https://docs.astral.sh/uv/guides/integration/docker/ for available images
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim

WORKDIR /workspace

# copy project source
COPY . .

# install dependencies with uv
RUN uv sync --frozen --all-extras
