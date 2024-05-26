# Changelog

## [4.5.0](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.4.1...testcontainers-v4.5.0) (2024-05-25)


### Features

* **core:** Private registry ([#566](https://github.com/testcontainers/testcontainers-python/issues/566)) ([59fbcfa](https://github.com/testcontainers/testcontainers-python/commit/59fbcfaf512d1f094e6d8346d45766e810ee2d44))


### Bug Fixes

* added types to exec & tc_properties_get_tc_host ([#561](https://github.com/testcontainers/testcontainers-python/issues/561)) ([9eabb79](https://github.com/testcontainers/testcontainers-python/commit/9eabb79f213cfb6d8e60173ff4c40f580ae0972a))
* on windows, DockerCompose.get_service_host returns an unusable "0.0.0.0" - adjust to 127.0.0.1 ([#457](https://github.com/testcontainers/testcontainers-python/issues/457)) ([2aa3d37](https://github.com/testcontainers/testcontainers-python/commit/2aa3d371647877db45eac1663814dcc99de0f6af))

## [4.4.1](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.4.0...testcontainers-v4.4.1) (2024-05-14)


### Bug Fixes

* Add memcached container ([#322](https://github.com/testcontainers/testcontainers-python/issues/322)) ([690b9b4](https://github.com/testcontainers/testcontainers-python/commit/690b9b4526dcdf930c0733c227009af208f47cda))
* Add selenium video support [#6](https://github.com/testcontainers/testcontainers-python/issues/6) ([#364](https://github.com/testcontainers/testcontainers-python/issues/364)) ([3c8006c](https://github.com/testcontainers/testcontainers-python/commit/3c8006cb6b94d074d2e33d27e972409886bcc7f3))
* **core:** add empty _configure to DockerContainer ([#556](https://github.com/testcontainers/testcontainers-python/issues/556)) ([08916c8](https://github.com/testcontainers/testcontainers-python/commit/08916c8fa29c835bc5c62fdbdd26ac1546c0c061))
* **core:** remove version from compose tests ([#571](https://github.com/testcontainers/testcontainers-python/issues/571)) ([38946d4](https://github.com/testcontainers/testcontainers-python/commit/38946d41dacdc4985fc696a5d58cf7d97e367a1c))
* **keycloak:** add realm imports ([#565](https://github.com/testcontainers/testcontainers-python/issues/565)) ([f761b98](https://github.com/testcontainers/testcontainers-python/commit/f761b983613e16dc56e560a947247c01052c19f6))
* **mysql:** Add seed support in MySQL ([#552](https://github.com/testcontainers/testcontainers-python/issues/552)) ([396079a](https://github.com/testcontainers/testcontainers-python/commit/396079a5af4c550084df2be5037a0ff52cd9fb5a))
* url quote passwords ([#549](https://github.com/testcontainers/testcontainers-python/issues/549)) ([6c5d227](https://github.com/testcontainers/testcontainers-python/commit/6c5d227730d415111c54e7ea3cb5d86b549cc901))

## [4.4.0](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.3.3...testcontainers-v4.4.0) (2024-04-17)


### Features

* **labels:** Add common testcontainers labels ([#519](https://github.com/testcontainers/testcontainers-python/issues/519)) ([e04b7ac](https://github.com/testcontainers/testcontainers-python/commit/e04b7ac78ccf6b79fce75ebd3a4626e00d764aa9))
* **network:** Add network context manager ([#367](https://github.com/testcontainers/testcontainers-python/issues/367)) ([11964de](https://github.com/testcontainers/testcontainers-python/commit/11964deb9e84c0559a391280202811b83a065ab8))


### Bug Fixes

* **core:** [#486](https://github.com/testcontainers/testcontainers-python/issues/486) for colima delay for port avail for connect ([#543](https://github.com/testcontainers/testcontainers-python/issues/543)) ([90bb780](https://github.com/testcontainers/testcontainers-python/commit/90bb780c30f42d3cfa2f724fb9ca3b6048d1dd9f))
* **core:** add TESTCONTAINERS_HOST_OVERRIDE as alternative to TC_HOST ([#384](https://github.com/testcontainers/testcontainers-python/issues/384)) ([8073874](https://github.com/testcontainers/testcontainers-python/commit/807387425913906b214f09c141a0bd0c337d788a))
* **dependencies:** remove usage of `sqlalchemy` in DB extras. Add default wait timeout for `wait_for_logs` ([#525](https://github.com/testcontainers/testcontainers-python/issues/525)) ([fefb9d0](https://github.com/testcontainers/testcontainers-python/commit/fefb9d0845bf6e0cbddad6868da5336b5b82bcb0))
* tests for Kafka container running on ARM64 CPU ([#536](https://github.com/testcontainers/testcontainers-python/issues/536)) ([29b5179](https://github.com/testcontainers/testcontainers-python/commit/29b51790ba31acf732eb5f017108bcb6622468f9))

## [4.3.3](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.3.2...testcontainers-v4.3.3) (2024-04-09)


### Bug Fixes

* missing typing-extensions dependency ([#534](https://github.com/testcontainers/testcontainers-python/issues/534)) ([ef86d15](https://github.com/testcontainers/testcontainers-python/commit/ef86d15f5c63159dcbeb3dbefe9b8fa1964177d9)), closes [#533](https://github.com/testcontainers/testcontainers-python/issues/533)

## [4.3.2](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.3.1...testcontainers-v4.3.2) (2024-04-08)


### Bug Fixes

* **core:** Improve typing for common container usage scenarios ([#523](https://github.com/testcontainers/testcontainers-python/issues/523)) ([d5b8553](https://github.com/testcontainers/testcontainers-python/commit/d5b855323be06f8d1395dd480a347f0efef75703))
* **core:** make config editable to avoid monkeypatching.1 ([#532](https://github.com/testcontainers/testcontainers-python/issues/532)) ([3be6da3](https://github.com/testcontainers/testcontainers-python/commit/3be6da335ba2026b4800dfd6a19cda4ca8e52be8))
* **vault:** add support for HashiCorp Vault container ([#366](https://github.com/testcontainers/testcontainers-python/issues/366)) ([1326278](https://github.com/testcontainers/testcontainers-python/commit/13262785dedf32a97e392afc1a758616995dc9d9))

## [4.3.1](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.3.0...testcontainers-v4.3.1) (2024-04-02)


### Bug Fixes

* **core:** env vars not being respected due to constructor call ([#524](https://github.com/testcontainers/testcontainers-python/issues/524)) ([4872ea5](https://github.com/testcontainers/testcontainers-python/commit/4872ea5759347e10150c0d80e4e7bbce3d59c410)), closes [#521](https://github.com/testcontainers/testcontainers-python/issues/521)
* Pin MongoDB images and improve test coverage for maintained versions ([#448](https://github.com/testcontainers/testcontainers-python/issues/448)) ([b5c7a1b](https://github.com/testcontainers/testcontainers-python/commit/b5c7a1b95af5470ee1b5109ed1fb8e1b3af52cf7))

## [4.3.0](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.2.0...testcontainers-v4.3.0) (2024-04-01)


### Features

* **client:** Add custom User-Agent in Docker client as `tc-python/&lt;version&gt;` ([#507](https://github.com/testcontainers/testcontainers-python/issues/507)) ([dd55082](https://github.com/testcontainers/testcontainers-python/commit/dd55082991b3405038a90678a39e8c815f0d1fc8))


### Bug Fixes

* Add CassandraContainer ([#476](https://github.com/testcontainers/testcontainers-python/issues/476)) ([507e466](https://github.com/testcontainers/testcontainers-python/commit/507e466a1fa9ac64c254ceb9ae0d57f6bfd8c89d))
* add chroma container ([#515](https://github.com/testcontainers/testcontainers-python/issues/515)) ([0729bf4](https://github.com/testcontainers/testcontainers-python/commit/0729bf4af957f8b6638cc204b108358745c0cfc9))
* Add Weaviate module ([#492](https://github.com/testcontainers/testcontainers-python/issues/492)) ([90762e8](https://github.com/testcontainers/testcontainers-python/commit/90762e817bf49de6d6366212fb48e7edb67ab0c6))
* **cassandra:** make cassandra dependency optional/test-only ([#518](https://github.com/testcontainers/testcontainers-python/issues/518)) ([bddbaeb](https://github.com/testcontainers/testcontainers-python/commit/bddbaeb20cbd147c429f8020395355402b8a7268))
* **core:** allow setting docker command path for docker compose ([#512](https://github.com/testcontainers/testcontainers-python/issues/512)) ([63fcd52](https://github.com/testcontainers/testcontainers-python/commit/63fcd52ec2d6ded5f6413166a3690c1138e4dae0))
* **google:** add support for Datastore emulator ([#508](https://github.com/testcontainers/testcontainers-python/issues/508)) ([3d891a5](https://github.com/testcontainers/testcontainers-python/commit/3d891a5ec62944d01d1bf3d6f70e6aec83f6e516))
* Improved Oracle DB module ([#363](https://github.com/testcontainers/testcontainers-python/issues/363)) ([6e6d8e3](https://github.com/testcontainers/testcontainers-python/commit/6e6d8e3c919be3efa581704868193e66da54acf3))
* inconsistent test runs for community modules ([#497](https://github.com/testcontainers/testcontainers-python/issues/497)) ([914f1e5](https://github.com/testcontainers/testcontainers-python/commit/914f1e55bcb3b10260788c3affb8426f77eb9036))
* **kafka:** Add redpanda testcontainer module ([#441](https://github.com/testcontainers/testcontainers-python/issues/441)) ([451d278](https://github.com/testcontainers/testcontainers-python/commit/451d27865873bb75f4a09a26442572745408d013))
* **kafka:** wait_for_logs in kafka container to reduce lib requirement ([#377](https://github.com/testcontainers/testcontainers-python/issues/377)) ([909107b](https://github.com/testcontainers/testcontainers-python/commit/909107b221417a39516f961364beb518d2756f45))
* **keycloak:** container should use dedicated API endpoints to determine container readiness ([#490](https://github.com/testcontainers/testcontainers-python/issues/490)) ([2e27225](https://github.com/testcontainers/testcontainers-python/commit/2e272253148797759748bd40c42f797697d3163f))
* **nats:** Client-Free(ish) NATS container ([#462](https://github.com/testcontainers/testcontainers-python/issues/462)) ([302c73d](https://github.com/testcontainers/testcontainers-python/commit/302c73ddaa7a6b5bc071ab0cc36d15461cae348b))
* **new:** add a new Docker Registry test container ([#389](https://github.com/testcontainers/testcontainers-python/issues/389)) ([0f554fb](https://github.com/testcontainers/testcontainers-python/commit/0f554fbaa9511e0221806f57de971abedf1c0bf2))
* pass doctests, s/doctest/doctests/, run them in gha, s/asyncpg/psycopg/ in doctest, fix keycloak flakiness: wait for first user ([#505](https://github.com/testcontainers/testcontainers-python/issues/505)) ([545240d](https://github.com/testcontainers/testcontainers-python/commit/545240dfdcb2a565ad7cef0e9813f03b9b6f910e))
* pass updated keyword args to Publisher/Subscriber client in google/pubsub [#161](https://github.com/testcontainers/testcontainers-python/issues/161) ([#164](https://github.com/testcontainers/testcontainers-python/issues/164)) ([8addc11](https://github.com/testcontainers/testcontainers-python/commit/8addc111c94826c2a619a0880d48550673f4d7b9))
* Qdrant module ([#463](https://github.com/testcontainers/testcontainers-python/issues/463)) ([e8876f4](https://github.com/testcontainers/testcontainers-python/commit/e8876f422abeb29a7236f2174f7e7a324b7d26cb))
* remove accidentally added pip in dev dependencies ([#516](https://github.com/testcontainers/testcontainers-python/issues/516)) ([dee20a7](https://github.com/testcontainers/testcontainers-python/commit/dee20a76c88445b911d38b4704c2380114a66794))
* **ryuk:** Enable Ryuk test suite. Ryuk image 0.5.1 -&gt; 0.7.0. Add RYUK_RECONNECTION_TIMEOUT env variable ([#509](https://github.com/testcontainers/testcontainers-python/issues/509)) ([472b2c2](https://github.com/testcontainers/testcontainers-python/commit/472b2c24aec232a04c00dd7dcd9a9f05f2dfaa66))

## [4.2.0](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.1.0...testcontainers-v4.2.0) (2024-03-24)


### Features

* support influxdb ([#413](https://github.com/testcontainers/testcontainers-python/issues/413)) ([13742a5](https://github.com/testcontainers/testcontainers-python/commit/13742a5dc448c80914953c21f8f2b01177c3fa6c))


### Bug Fixes

* **arangodb:** tests to pass on ARM CPUs - change default image to 3.11.x where ARM image is published ([#479](https://github.com/testcontainers/testcontainers-python/issues/479)) ([7b58a50](https://github.com/testcontainers/testcontainers-python/commit/7b58a50f3a8703c5d5e974a4ff20bc8e52ae93c8))
* **core:** DinD issues [#141](https://github.com/testcontainers/testcontainers-python/issues/141), [#329](https://github.com/testcontainers/testcontainers-python/issues/329) ([#368](https://github.com/testcontainers/testcontainers-python/issues/368)) ([b10d916](https://github.com/testcontainers/testcontainers-python/commit/b10d916848cccc016fc457333f7b382b18a7b3ef))
* **core:** raise an exception when docker compose fails to start [#258](https://github.com/testcontainers/testcontainers-python/issues/258) ([#485](https://github.com/testcontainers/testcontainers-python/issues/485)) ([d61af38](https://github.com/testcontainers/testcontainers-python/commit/d61af383def6eadcd7f2b5ba667eb587c6cc84f1))
* **core:** use auto_remove=True with reaper instance ([#499](https://github.com/testcontainers/testcontainers-python/issues/499)) ([274a400](https://github.com/testcontainers/testcontainers-python/commit/274a4002600ae70662a5785c7a903cf8846b2ffc))
* **docs:** update the non-existent main.yml badge ([#493](https://github.com/testcontainers/testcontainers-python/issues/493)) ([1d10c1c](https://github.com/testcontainers/testcontainers-python/commit/1d10c1ca8c8163b8d68338e1d50d0e26d7b0515e))
* Fix the return type of `DockerContainer.get_logs` ([#487](https://github.com/testcontainers/testcontainers-python/issues/487)) ([cd72f68](https://github.com/testcontainers/testcontainers-python/commit/cd72f6896db3eb1fd5ea60f9c051cb719568a12f))
* **keycloak:** tests on aarch64, use image from [jboss -&gt; quay], change supported version [16+ -> 18+] ([#480](https://github.com/testcontainers/testcontainers-python/issues/480)) ([5758310](https://github.com/testcontainers/testcontainers-python/commit/5758310532b8a8e1303a24bc534fa8aeb0f75eb2))
* **postgres:** doctest ([#473](https://github.com/testcontainers/testcontainers-python/issues/473)) ([c9c6f92](https://github.com/testcontainers/testcontainers-python/commit/c9c6f92348299a2cc04988af8d69a53a23a7c7d5))
* read the docs build works again ([#496](https://github.com/testcontainers/testcontainers-python/issues/496)) ([dfd1781](https://github.com/testcontainers/testcontainers-python/commit/dfd17814a7fc9ede510ae17569004bd92f2a6fa6))
* readthedocs build - take 1 ([#495](https://github.com/testcontainers/testcontainers-python/issues/495)) ([b3b9901](https://github.com/testcontainers/testcontainers-python/commit/b3b990159154857239e2fb86da3cb85a6a13ab8e))

## [4.1.0](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.0.1...testcontainers-v4.1.0) (2024-03-19)


### Features

* **reliability:** integrate the ryuk container for better container cleanup ([#314](https://github.com/testcontainers/testcontainers-python/issues/314)) ([d019874](https://github.com/testcontainers/testcontainers-python/commit/d0198744c3bdc97a7fe41879b54acb2f5ee7becb))


### Bug Fixes

* changelog after release-please ([#469](https://github.com/testcontainers/testcontainers-python/issues/469)) ([dcb4f68](https://github.com/testcontainers/testcontainers-python/commit/dcb4f6842cbfe6e880a77b0d4aabb3f396c6dc19))
* **configuration:** strip whitespaces when reading .testcontainers.properties ([#474](https://github.com/testcontainers/testcontainers-python/issues/474)) ([ade144e](https://github.com/testcontainers/testcontainers-python/commit/ade144ee2888d4044ac0c1dc627f47da92789e06))
* try to fix release-please by setting a bootstrap sha ([#472](https://github.com/testcontainers/testcontainers-python/issues/472)) ([ca65a91](https://github.com/testcontainers/testcontainers-python/commit/ca65a916b719168c57c174d2af77d45fd026ec05))

## [4.0.1](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.0.0...testcontainers-v4.0.1) (2024-03-11)


### Features

* **postgres:** Remove SqlAlchemy dependency from postgres container ([#445](https://github.com/testcontainers/testcontainers-python/issues/445)) ([f30eb1d](https://github.com/testcontainers/testcontainers-python/commit/f30eb1d4c98d3cc20582573b5def76d533a38b80))


### Bug Fixes

* **clickhouse:** clickhouse waiting ([#428](https://github.com/testcontainers/testcontainers-python/issues/428)) ([902a5a3](https://github.com/testcontainers/testcontainers-python/commit/902a5a3d5112317782db6a9a91d9fc4bfe5701af))
* Close docker client when stopping the docker container ([#380](https://github.com/testcontainers/testcontainers-python/issues/380)) ([efb1683](https://github.com/testcontainers/testcontainers-python/commit/efb16832dc0be75014c7388f9b241ae0be36ddd4))
* failing tests for elasticsearch on machines with ARM CPU ([#454](https://github.com/testcontainers/testcontainers-python/issues/454)) ([701b23a](https://github.com/testcontainers/testcontainers-python/commit/701b23a7a0e4632db13e29c52141f9efc67467a1))
* go back to 4.0.1 ([#465](https://github.com/testcontainers/testcontainers-python/issues/465)) ([1ac8c24](https://github.com/testcontainers/testcontainers-python/commit/1ac8c24d58e93ead951342dcc36e6f8cee2b5fa7))
* **mongodb:** waiting for container to start (it was not waiting at all before?) ([#461](https://github.com/testcontainers/testcontainers-python/issues/461)) ([2c4f171](https://github.com/testcontainers/testcontainers-python/commit/2c4f171b001f0c45ff84199adf419c7a70ed81c5))
* unclosed socket warning in db containers ([#378](https://github.com/testcontainers/testcontainers-python/issues/378)) ([cd90aa7](https://github.com/testcontainers/testcontainers-python/commit/cd90aa7310142059cb00f66bbc3693aedf5ddcb2))
* Update the copyright header for readthedocs ([#341](https://github.com/testcontainers/testcontainers-python/issues/341)) ([5bef18a](https://github.com/testcontainers/testcontainers-python/commit/5bef18a51360a2d74ba393f86b753abdf9ec5636))

## [4.0.1](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.0.0...testcontainers-v4.0.1) (2024-03-11)


### Features

* **postgres:** Remove SqlAlchemy dependency from postgres container ([#445](https://github.com/testcontainers/testcontainers-python/issues/445)) ([f30eb1d](https://github.com/testcontainers/testcontainers-python/commit/f30eb1d4c98d3cc20582573b5def76d533a38b80))


### Bug Fixes

* **clickhouse:** clickhouse waiting ([#428](https://github.com/testcontainers/testcontainers-python/issues/428)) ([902a5a3](https://github.com/testcontainers/testcontainers-python/commit/902a5a3d5112317782db6a9a91d9fc4bfe5701af))
* Close docker client when stopping the docker container ([#380](https://github.com/testcontainers/testcontainers-python/issues/380)) ([efb1683](https://github.com/testcontainers/testcontainers-python/commit/efb16832dc0be75014c7388f9b241ae0be36ddd4))
* failing tests for elasticsearch on machines with ARM CPU ([#454](https://github.com/testcontainers/testcontainers-python/issues/454)) ([701b23a](https://github.com/testcontainers/testcontainers-python/commit/701b23a7a0e4632db13e29c52141f9efc67467a1))
* **mongodb:** waiting for container to start (it was not waiting at all before?) ([#461](https://github.com/testcontainers/testcontainers-python/issues/461)) ([2c4f171](https://github.com/testcontainers/testcontainers-python/commit/2c4f171b001f0c45ff84199adf419c7a70ed81c5))
* unclosed socket warning in db containers ([#378](https://github.com/testcontainers/testcontainers-python/issues/378)) ([cd90aa7](https://github.com/testcontainers/testcontainers-python/commit/cd90aa7310142059cb00f66bbc3693aedf5ddcb2))
* Update the copyright header for readthedocs ([#341](https://github.com/testcontainers/testcontainers-python/issues/341)) ([5bef18a](https://github.com/testcontainers/testcontainers-python/commit/5bef18a51360a2d74ba393f86b753abdf9ec5636))

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
