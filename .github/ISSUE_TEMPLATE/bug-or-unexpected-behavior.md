---
name: Bug or unexpected behavior
about: Create a report to help us improve.
title: 'Bug: '
labels: bug
assignees: ''

---

**Describe the bug**

A clear and concise description of what the bug is. What did you expect to happen? What happened instead?

**To Reproduce**

Provide a self-contained code snippet that illustrates the bug or unexpected behavior. Ideally, send a Pull Request to illustrate with a test that illustrates the problem.

```python
raise RuntimeError("something went wrong")
```

**Runtime environment**

Provide a summary of your runtime environment. Which operating system, python version, and docker version are you using? What is the version of `testcontainers-python` you are using? You can run the following commands to get the relevant information.

```bash
# Get the operating system information (on a unix os).
$ uname -a
# Get the python version.
$ python --version
# Get the docker version and other docker information.
$ docker info
# Get all python packages.
$ pip freeze
```
