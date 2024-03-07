# Changelog

## [4.0.0](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v3.7.1...testcontainers-v4.0.0) (2024-03-06)


### ⚠ BREAKING CHANGES

* **compose:** implement compose v2 with improved typing ([#426](https://github.com/testcontainers/testcontainers-python/issues/426))
* **core:** add support for `tc.host` and de-prioritise `docker:dind` ([#388](https://github.com/testcontainers/testcontainers-python/issues/388))

### Features

* **build:** use poetry and organise modules ([#408](https://github.com/testcontainers/testcontainers-python/issues/408)) ([6c69583](https://github.com/testcontainers/testcontainers-python/commit/6c695835520bdcbf9824e8cefa00f7613d2a7cb9))
* **compose:** allow running specific services in compose ([f61dcda](https://github.com/testcontainers/testcontainers-python/commit/f61dcda8bd7ea329cd3c836b6d6e2f0bd990335d))
* **compose:** implement compose v2 with improved typing ([#426](https://github.com/testcontainers/testcontainers-python/issues/426)) ([5356caf](https://github.com/testcontainers/testcontainers-python/commit/5356caf2de056313a5b3f2805ed80e6a23b027a8))
* **core:** add support for `tc.host` and de-prioritise `docker:dind` ([#388](https://github.com/testcontainers/testcontainers-python/issues/388)) ([2db8e6d](https://github.com/testcontainers/testcontainers-python/commit/2db8e6d123d42b57309408dd98ba9a06acc05c4b))
* **redis:** support AsyncRedisContainer ([#442](https://github.com/testcontainers/testcontainers-python/issues/442)) ([cc4cb37](https://github.com/testcontainers/testcontainers-python/commit/cc4cb3762802dc75b0801727d8b1f1a1c56b7f50))
* **release:** automate release via release-please ([#429](https://github.com/testcontainers/testcontainers-python/issues/429)) ([30f859e](https://github.com/testcontainers/testcontainers-python/commit/30f859eb1535acd6e93c331213426e1319ee9a47))


### Bug Fixes

* Added URLError to exceptions to wait for in elasticsearch ([0f9ad24](https://github.com/testcontainers/testcontainers-python/commit/0f9ad24f2c0df362ee15b81ce8d7d36b9f98e6e1))
* **build:** add `pre-commit` as a dev dependency to simplify local dev and CI ([#438](https://github.com/testcontainers/testcontainers-python/issues/438)) ([1223583](https://github.com/testcontainers/testcontainers-python/commit/1223583d8fc3a1ab95441d82c7e1ece57f026fbf))
* **build:** early exit strategy for modules ([#437](https://github.com/testcontainers/testcontainers-python/issues/437)) ([7358b49](https://github.com/testcontainers/testcontainers-python/commit/7358b4919c1010315a384a8f0fe2860e5a0ca6b4))
* changed files breaks on main ([#422](https://github.com/testcontainers/testcontainers-python/issues/422)) ([3271357](https://github.com/testcontainers/testcontainers-python/commit/32713578dcf07f672a87818e00562b58874b4a52))
* flaky garbage collection resulting in testing errors ([#423](https://github.com/testcontainers/testcontainers-python/issues/423)) ([b535ea2](https://github.com/testcontainers/testcontainers-python/commit/b535ea255bcaaa546f8cda7b2b17718c1cc7f3ca))
* rabbitmq readiness probe ([#375](https://github.com/testcontainers/testcontainers-python/issues/375)) ([71cb75b](https://github.com/testcontainers/testcontainers-python/commit/71cb75b281df55ece4d5caf5d487059a7f38c34f))
* **release:** prove that the release process updates the version ([#444](https://github.com/testcontainers/testcontainers-python/issues/444)) ([87b5873](https://github.com/testcontainers/testcontainers-python/commit/87b5873c1ec3a3e4e74742417d6068fa86cf1762))
* test linting issue ([427c9b8](https://github.com/testcontainers/testcontainers-python/commit/427c9b841c2f6f516ec6cb74d5bd2839cb1939f4))


### Documentation

* Sphinx - Add title to each doc page  ([#443](https://github.com/testcontainers/testcontainers-python/issues/443)) ([750e12a](https://github.com/testcontainers/testcontainers-python/commit/750e12a41172ce4aaf045c61dec33d318dc3c2f6))
