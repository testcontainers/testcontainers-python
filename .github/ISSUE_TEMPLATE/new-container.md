---
name: New Container
about: Tell the Testcontainers-Python team about a container you'd like to have support for.
title: 'New Container: '
labels: '🚀 enhancement'
assignees: ''

---

<!-- feel free to remove any irrelevant section(s) below -->

**What is the new container you'd like to have?**

Please link some docker containers as well as documentation to the benefits of having this container.

**Why not just use a generic container for this?**

Please describe why the `DockerContainer("my-image:latest")` approach is not useful enough.

Having a dedicated `TestContainer` usually means the need for some or all of these:
- complicated setup/configuration
- the wait strategy is complex for the container, usually more than just an http wait

**Other references:**

Include any other relevant reading material about the enhancement.
