# Python versions

The library supports Python >= 3.9, < 4.0.

## Updating your Python version

There are several common approaches for managing and isolating your Python environment when using Testcontainers (or any Python project). Each has its own trade-offs in terms of reproducibility, ease of use, and integration with tooling:

### venv (built-in virtual environments)

#### What it is

Python’s built-in way to create lightweight environments.

#### How to use

```bash
python3 -m venv .venv # create an env in “.venv”
source .venv/bin/activate # on Unix/macOS
.venv\Scripts\activate # on Windows
pip install -r requirements.txt
```

| Pros                                      | Cons                                               |
| ----------------------------------------- | -------------------------------------------------- |
| No extra dependencies                     | You still manage `requirements.txt` by hand        |
| Very lightweight                          | Doesn’t provide lockfiles or dependency resolution |
| Works everywhere Python 3.3+ is installed |                                                    |

### virtualenv (stand-alone)

#### What it is

A more mature alternative to venv, sometimes faster and with more features.

#### How to use

```bash
pip install virtualenv
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```

| Pros                                                                        | Cons                                                 |
| --------------------------------------------------------------------------- | ---------------------------------------------------- |
| Slightly more flexible than `venv` (e.g. can target different interpreters) | Still manual management of versions and dependencies |

### pipenv

#### What it is

A higher-level tool combining environment creation with Pipfile dependency management.

#### How to use

```bash
pip install pipenv
pipenv install --dev testcontainers
pipenv shell
```

Dependencies live in Pipfile; exact versions locked in Pipfile.lock.

| Pros                                      | Cons                                                |
| ----------------------------------------- | --------------------------------------------------- |
| Automatic creation of a virtualenv        | Can be slower, historically some performance quirks |
| Lockfile for reproducible installs        |                                                     |
| `pipenv run …` to avoid activating shells |                                                     |

### poetry

#### What it is

A modern dependency manager and packaging tool, with built-in virtualenv support.

#### How to use

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry init # walk you through pyproject.toml creation
poetry add --dev testcontainers
poetry shell
```

Your Python version constraints and dependencies are in pyproject.toml; lockfile is poetry.lock.

| Pros                                                | Cons                                                  |
| --------------------------------------------------- | ----------------------------------------------------- |
| Elegant TOML-based config                           | A bit of a learning curve if you’re used to plain Pip |
| Creates truly reproducible environments             |                                                       |
| Supports publishing packages to PyPI out of the box |                                                       |

### conda / mamba

#### What it is

Cross-language environment and package manager (Python/R/C++).

#### How to use

```bash
conda create -n tc-env python=3.10
conda activate tc-env
conda install pip
pip install testcontainers
```

Or with Mamba for faster solves:

```bash
mamba install pip
mamba install -c conda-forge testcontainers
```

| Pros                                                            | Cons                        |
| --------------------------------------------------------------- | --------------------------- |
| Manages non-Python dependencies easily (e.g., system libraries) | Larger disk footprint       |
| Reproducible YAML environment files (`environment.yml`)         | Less “pure” Python workflow |

### Docker-based environments

#### What it is

Run your tests inside a Docker image, so everything (even Python itself) is containerized.

#### How to use

```bash
FROM python:3.10-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-root
COPY . .
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-q"]
```

| Pros                                                 | Cons                                                |
| ---------------------------------------------------- | --------------------------------------------------- |
| True isolation from host machine (including OS libs) | Slower startup/testing cycle                        |
| Easy to share exact environment via Dockerfile       | Extra complexity if you’re not already Docker-savvy |

### tox for multi-env testing

#### What it is

A tool to automate testing across multiple Python versions/environments.

#### How to use

```bash
# tox.ini

[tox]
envlist = py39,py310,py311

[testenv]
deps = pytest
testcontainers
commands = pytest
```

| Pros                                                      | Cons                         |
| --------------------------------------------------------- | ---------------------------- |
| Ensures compatibility across multiple Python interpreters | Adds another layer of config |
| Isolates each test run in its own venv                    |                              |

## Choosing the Right Tool

| Tool         | Lockfile? | Built-in Env | Cross-Platform | Non-Python Deps | Reproducibility |
| ------------ | --------- | ------------ | -------------- | --------------- | --------------- |
| `venv`       | No        | Yes          | Yes            | No              | Low             |
| `virtualenv` | No        | Yes          | Yes            | No              | Low             |
| `pipenv`     | Yes       | Yes          | Yes            | No              | Medium          |
| `poetry`     | Yes       | Yes          | Yes            | No              | High            |
| `conda`      | Yes (YML) | Yes          | Yes            | Yes             | High            |
| Docker       | –         | Container    | Yes            | Yes             | Very High       |

## Next Steps

With any of these, once your environment is set up you can simply `pip install testcontainers` (or use Poetry’s `poetry add --dev testcontainers`) and begin writing your container-backed tests in Python.

See the [General Docker Requirements](docker.md) to continue
