echo "Running post-create-command.sh"

pre-commit install
poetry install --all-extras
