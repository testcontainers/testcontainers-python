# Required for expansion in dependencies.
.SECONDEXPANSION :
PYTHON_VERSIONS = 3.7 3.8 3.9 3.10
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
# All the requirements (without python version).
PACKAGE_REQUIREMENTS = $(addsuffix /requirements,${PACKAGES})
# All the requirements (with python version).
REQUIREMENTS = $(foreach v,${PYTHON_VERSIONS},$(addsuffix /${v}.txt,${PACKAGE_REQUIREMENTS}))

# Targets to build a distribution for each package.
dist: ${DISTRIBUTIONS}
${DISTRIBUTIONS} : %/dist : %/setup.py
	cd $* \
	&& python setup.py bdist_wheel \
	&& twine check dist/*

# Targets to run the test suite for each package.
tests : ${TESTS}
${TESTS} : %/tests :
	pytest -svx --cov-report=term-missing --cov=testcontainers.$* --tb=short $*/tests

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
image: requirements/${PYTHON_VERSION}.txt
	echo "DinD tests are not currently supported"
	false
	docker build --build-arg version=${PYTHON_VERSION} -t ${IMAGE} .

# Targets to run tests in docker containers
tests-dind : ${TESTS_DIND}

${TESTS_DIND} : %/tests-dind : image
	echo "DinD tests are not currently supported"
	false
	${RUN} -v /var/run/docker.sock:/var/run/docker.sock ${IMAGE} \
		bash -c "make $*/lint $*/tests"

# Target to build the documentation
docs :
	sphinx-build -nW . docs/_build

doctest : ${DOCTESTS}
	sphinx-build -b doctest . docs/_build

${DOCTESTS} : %/doctest :
	sphinx-build -b doctest -c doctests $* docs/_build

# Build all requirement files.
requirements : ${PACKAGE_REQUIREMENTS} docs/requirements.txt

# Build requirement files for a given package.
${PACKAGE_REQUIREMENTS} : %/requirements : $$(addprefix %/requirements/,$${PYTHON_VERSIONS:=.txt})

# Build requirement files for a given package and python version. This isn't pretty but Makefiles
# don't have particularly flexible variable handling. $(word 1,$(subst /, ,$*)) is the package and
# $(word 3,$(subst /, ,$*)) is the python version. We need to use double expansion $$ in the
# dependencies.
${REQUIREMENTS} : %.txt : $$(word 1,$$(subst /, ,%))/requirements.in $$(word 1,$$(subst /, ,%))/setup.py common_requirements.in
	mkdir -p $(dir $@)
	${RUN} -w /workspace -v `pwd`:/workspace --platform=linux/amd64 python:$(word 3,$(subst /, ,$*)) \
		bash -c "pip install pip-tools && pip-compile --resolver=backtracking -v --upgrade -o $@ common_requirements.in $(word 1,$(subst /, ,$*))/requirements.in"

docs/requirements.txt : docs/requirements.in */setup.py
	${RUN} -w /workspace -v `pwd`:/workspace --platform=linux/amd64 python:${PYTHON_VERSION} \
		bash -c "pip install pip-tools && pip-compile --resolver=backtracking -v --upgrade -o $@ common_requirements.in $<"

# Remove any generated files.
clean :
	rm -rf docs/_build
	rm -rf */build
	rm -rf */dist
	rm -rf */*.egg-info

# Targets that do not generate file-level artifacts.
.PHONY : clean dists ${DISTRIBUTIONS} docs doctests image tests ${TESTS}
