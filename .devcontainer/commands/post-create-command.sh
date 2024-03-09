echo "Running post-create-command.sh"

curl -sSL https://install.python-poetry.org | python3 -

poetry lock --no-update
poetry install --all-extras
