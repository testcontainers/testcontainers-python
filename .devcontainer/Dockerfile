FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm


COPY --chown=vscode:vscode .git-completion.sh /home/vscode/.git-completion.sh
COPY --chown=vscode:vscode .poetry-completion.sh /home/vscode/.poetry-completion.sh
RUN pip install pre-commit && \
apt update && apt install bash-completion  && \
curl -sSL https://install.python-poetry.org | POETRY_HOME=/home/vscode/.local python3 -


RUN  echo ' ' >> /home/vscode/.bashrc && \
echo '. ~/.git-completion.sh' >> /home/vscode/.bashrc && \
echo ' ' >> /home/vscode/.bashrc && \
echo '. ~/.poetry-completion.sh' >> /home/vscode/.bashrc
