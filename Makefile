PYTHON_VERSIONS = 3.9 3.10 3.11
PYTHON_VERSION ?= 3.10
IMAGE = testcontainers-python:${PYTHON_VERSION}
RUN = docker run --rm -it
# Get all directories that contain a setup.py and get the directory name.
PACKAGES = core $(addprefix modules/,$(notdir $(wildcard modules/*)))

# All */dist folders for each of the packages.
DISTRIBUTIONS = $(addsuffix /dist,${PACKAGES})
UPLOAD = $(addsuffix /upload,${PACKAGES})
# All */tests folders for each of the test suites.
TESTS = $(addsuffix /tests,$(filter-out meta,${PACKAGES}))
TESTS_DIND = $(addsuffix -dind,${TESTS})
DOCTESTS = $(addsuffix /doctests,$(filter-out modules/README.md,${PACKAGES}))
# All linting targets.
LINT = $(addsuffix /lint,${PACKAGES})

# Targets to build a distribution for each package.
dist: ${DISTRIBUTIONS}
${DISTRIBUTIONS} : %/dist : %/setup.py
	cd $* \
	&& python setup.py bdist_wheel \
	&& twine check dist/*

# Targets to run the test suite for each package.
tests : ${TESTS}
${TESTS} : %/tests :
	poetry run pytest -v --cov=testcontainers.$* $*/tests

# Target to lint the code.
lint:
	pre-commit run -a

# Targets to publish packages.
upload : ${UPLOAD}
${UPLOAD} : %/upload :
	if [ ${TWINE_REPOSITORY}-$* = testpypi-meta ]; then \
		echo "Cannot upload meta package to testpypi because of missing permissions."; \
	else \
		twine upload --non-interactive --skip-existing $*/dist/*; \
	fi

# Targets to build docker images
image:
	poetry export -f requirements.txt -o build/requirements.txt
	docker build --build-arg version=${PYTHON_VERSION} -t ${IMAGE} .

# Targets to run tests in docker containers
tests-dind : ${TESTS_DIND}

${TESTS_DIND} : %/tests-dind : image
	${RUN} -v /var/run/docker.sock:/var/run/docker.sock ${IMAGE} \
		bash -c "make $*/lint $*/tests"

# Target to build the documentation
docs :
	poetry run sphinx-build -nW . docs/_build

doctests : ${DOCTESTS}
	poetry run sphinx-build -b doctest . docs/_build

${DOCTESTS} : %/doctests :
	poetry run sphinx-build -b doctest -c doctests $* docs/_build

# Remove any generated files.
clean :
	rm -rf docs/_build
	rm -rf */build
	rm -rf */dist
	rm -rf */*.egg-info

# Targets that do not generate file-level artifacts.
.PHONY : clean dists ${DISTRIBUTIONS} docs doctests image tests ${TESTS}
