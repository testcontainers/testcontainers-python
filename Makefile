PYTHON_VERSIONS = 3.6 3.7 3.8
REQUIREMENTS = $(addprefix requirements/,${PYTHON_VERSIONS:=.txt})
TESTS = $(addprefix tests/,${PYTHON_VERSIONS})
IMAGES = $(addprefix image/,${PYTHON_VERSIONS})
ARCH = $(shell arch)
ifeq (${ARCH}, arm64)
	RUN = docker run --rm -it --platform linux/amd64
else
	RUN = docker run --rm -it
endif
.PHONY : docs

# Default target

default : tests/3.8


# Targets to build requirement files

requirements : ${REQUIREMENTS}

${REQUIREMENTS} : requirements/%.txt : requirements.in setup.py
	mkdir -p $(dir $@)
	${RUN} -w /workspace -v `pwd`:/workspace python:$* bash -c \
		"pip install pip-tools && pip-compile -v --upgrade -o $@ $<"


# Targets to build docker images

images : ${IMAGES}

${IMAGES} : image/% : requirements/%.txt
	docker build --build-arg version=$* -t testcontainers-python:$* .


# Targets to run tests in docker containers

tests : ${TESTS}

${TESTS} : tests/% : image/%
	${RUN} -v /var/run/docker.sock:/var/run/docker.sock testcontainers-python:$* bash -c \
		"flake8 && pytest -v ${ARGS}"

# Target to build the documentation

docs :
	sphinx-build -nW docs docs/_build/html
