PYTHON_VERSIONS = 3.7 3.8 3.9 3.10 3.11
PYTHON_VERSION ?= 3.10
IMAGE = testcontainers-python:${PYTHON_VERSION}
RUN = docker run --rm -it
# Get all directories that contain a setup.py and get the directory name.
PACKAGES = $(subst /,,$(dir $(wildcard */setup.py)))

# All */dist folders for each of the packages.
DISTRIBUTIONS = $(addsuffix /dist,${PACKAGES})
UPLOAD = $(addsuffix /upload,${PACKAGES})
# All */tests folders for each of the test suites.
TESTS = $(addsuffix /tests,$(filter-out meta,${PACKAGES}))
TESTS_DIND = $(addsuffix -dind,${TESTS})
DOCTESTS = $(addsuffix /doctest,$(filter-out meta,${PACKAGES}))
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
	pytest -svx --cov-report=term-missing --cov=testcontainers.$* --tb=short --strict-markers $*/tests

# Targets to lint the code.
lint : ${LINT}
${LINT} : %/lint :
	flake8 $*

# Targets to publish packages.
upload : ${UPLOAD}
${UPLOAD} : %/upload :
	if [ ${TWINE_REPOSITORY}-$* = testpypi-meta ]; then \
		echo "Cannot upload meta package to testpypi because of missing permissions."; \
	else \
		twine upload --non-interactive --skip-existing $*/dist/*; \
	fi

# Targets to build docker images
image: requirements/ubunut-latest-${PYTHON_VERSION}.txt
	docker build --build-arg version=${PYTHON_VERSION} -t ${IMAGE} .

# Targets to run tests in docker containers
tests-dind : ${TESTS_DIND}

${TESTS_DIND} : %/tests-dind : image
	${RUN} -v /var/run/docker.sock:/var/run/docker.sock ${IMAGE} \
		bash -c "make $*/lint $*/tests"

# Target to build the documentation
docs :
	sphinx-build -nW . docs/_build

doctest : ${DOCTESTS}
	sphinx-build -b doctest . docs/_build

${DOCTESTS} : %/doctest :
	sphinx-build -b doctest -c doctests $* docs/_build

# Remove any generated files.
clean :
	rm -rf docs/_build
	rm -rf */build
	rm -rf */dist
	rm -rf */*.egg-info

# Targets that do not generate file-level artifacts.
.PHONY : clean dists ${DISTRIBUTIONS} docs doctests image tests ${TESTS}
