PYTHON_VERSIONS = 3.9 3.10 3.11
PYTHON_VERSION ?= 3.10
IMAGE = testcontainers-python:${PYTHON_VERSION}
RUN = docker run --rm -it
TEST_NAMES := $(notdir $(wildcard tests/*))

TESTS := $(addprefix tests/,$(TEST_NAMES))
TESTS_DIND = $(addsuffix -dind,${TESTS})

dist:
	poetry build \
	&& poetry run twine check dist/*.tar.gz

# Targets to run the test suite for each package.
tests : ${TESTS}
${TESTS} : tests/% :
	poetry run pytest -v --cov=testcontainers.$* tests/$*

# Target to lint the code.
lint:
	pre-commit run -a

# Targets to publish packages.
upload :
	poetry run twine upload --non-interactive --skip-existing dist/*

# Targets to build docker images
image:
	mkdir -p build/
	poetry export -f requirements.txt -o build/requirements.txt
	docker build --build-arg version=${PYTHON_VERSION} -t ${IMAGE} .

# Targets to run tests in docker containers
tests-dind : ${TESTS_DIND}

${TESTS_DIND} : tests/%-dind : image
	${RUN} -v /var/run/docker.sock:/var/run/docker.sock ${IMAGE} \
		bash -c "make lint tests/$*"

# Target to build the documentation
docs :
	poetry run sphinx-build -nW . docs/_build

doctest :
	poetry run sphinx-build -b doctest . docs/_build

# Remove any generated files.
clean :
	rm -rf docs/_build
	rm -rf build
	rm -rf dist
	rm -rf */*.egg-info

# Targets that do not generate file-level artifacts.
.PHONY : clean dists docs doctests image tests ${TESTS}
