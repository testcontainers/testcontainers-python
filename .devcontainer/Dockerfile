FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm


RUN \
    apt update && apt install bash-completion -y && \
    pip install pre-commit && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=/home/vscode/.local python3 -


RUN  \
    echo >> /home/vscode/.bashrc && \
    # add completions to bashrc
    # see how ubuntu does it for reference:
    # https://git.launchpad.net/ubuntu/+source/base-files/tree/share/dot.bashrc
    # https://stackoverflow.com/a/68566555
    echo 'if [ -f /etc/bash_completion ] && ! shopt -oq posix; then' >> /home/vscode/.bashrc && \
    echo '    . /etc/bash_completion' >> /home/vscode/.bashrc && \
    echo 'fi' >> /home/vscode/.bashrc && \
    echo >> /home/vscode/.bashrc && \
    echo '. <(poetry completions)' >> /home/vscode/.bashrc
