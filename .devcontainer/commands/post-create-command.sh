echo "Running post-create-command.sh"

pre-commit install
uv sync --all-extras
