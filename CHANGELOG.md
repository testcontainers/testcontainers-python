# Changelog

## [4.8.2](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.8.1...testcontainers-v4.8.2) (2024-09-27)


### Bug Fixes

* **core:** Reorganize core tests and improve ([#693](https://github.com/testcontainers/testcontainers-python/issues/693)) ([f1665f3](https://github.com/testcontainers/testcontainers-python/commit/f1665f3aa66eff443923d897ec553e09e47f6a78))
* **core:** Typing in auth ([#691](https://github.com/testcontainers/testcontainers-python/issues/691)) ([66726b6](https://github.com/testcontainers/testcontainers-python/commit/66726b656ab8fd18a69771ff2ee2a3fd8ca959b0))
* **core:** Typing in config + utils ([#692](https://github.com/testcontainers/testcontainers-python/issues/692)) ([794a22e](https://github.com/testcontainers/testcontainers-python/commit/794a22e22362227ccfc0b2acd18130196e25775d))
* **keycloak:** Add support for Keycloak version &gt;=25 ([#694](https://github.com/testcontainers/testcontainers-python/issues/694)) ([62bd0de](https://github.com/testcontainers/testcontainers-python/commit/62bd0debffdb762714de853a069e3b63414fa789))
* mysql typo ([#705](https://github.com/testcontainers/testcontainers-python/issues/705)) ([85d6078](https://github.com/testcontainers/testcontainers-python/commit/85d6078f9bcc99050c0173e459208402aa4f5026)), closes [#689](https://github.com/testcontainers/testcontainers-python/issues/689)
* **opensearch:** add support for admin_password in &gt;= 2.12 ([#697](https://github.com/testcontainers/testcontainers-python/issues/697)) ([935693e](https://github.com/testcontainers/testcontainers-python/commit/935693e01686fea9bf3201cd8c70b3e617bda2ee))
* postgres use psql instead of logs ([#704](https://github.com/testcontainers/testcontainers-python/issues/704)) ([4365754](https://github.com/testcontainers/testcontainers-python/commit/436575410a2906a695b96af66ff55c9ccb8e09a7))
* **tests:** Missing artifacts (include-hidden-files) ([#699](https://github.com/testcontainers/testcontainers-python/issues/699)) ([8f1165d](https://github.com/testcontainers/testcontainers-python/commit/8f1165dd79ee0dcf16f37f2d186cbc3d47bc11bc))

## [4.8.1](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.8.0...testcontainers-v4.8.1) (2024-08-18)


### Bug Fixes

* **generic:** Update the FastAPI install on genric module doctest samples ([#686](https://github.com/testcontainers/testcontainers-python/issues/686)) ([5216b02](https://github.com/testcontainers/testcontainers-python/commit/5216b0241a27afe3419f5c4a6d500dc27154ddd4))
* **mssql:** use glob to find mssql-tools folder since it moves ([#685](https://github.com/testcontainers/testcontainers-python/issues/685)) ([4912725](https://github.com/testcontainers/testcontainers-python/commit/4912725c2a54a9edce046416fbf11e089cc03cb0)), closes [#666](https://github.com/testcontainers/testcontainers-python/issues/666)
* wait_for_logs can now fail early when the container stops ([#682](https://github.com/testcontainers/testcontainers-python/issues/682)) ([925329d](https://github.com/testcontainers/testcontainers-python/commit/925329d8d2df78437a491a29b707d5ac97e7b734))


### Documentation

* Add a more advance usecase documentation for ServerContainer ([#688](https://github.com/testcontainers/testcontainers-python/issues/688)) ([2cf5a9f](https://github.com/testcontainers/testcontainers-python/commit/2cf5a9fbe6db3fa4254a5bb54e67412ec2d08488))

## [4.8.0](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.7.2...testcontainers-v4.8.0) (2024-08-14)


### Features

* Adding support for Cassandra and Scylla ([#167](https://github.com/testcontainers/testcontainers-python/issues/167)) ([2d8bc11](https://github.com/testcontainers/testcontainers-python/commit/2d8bc11c8e151af66456ebad156afc4a87822676))
* **compose:** ability to retain volumes when using context manager ([#659](https://github.com/testcontainers/testcontainers-python/issues/659)) ([e1e3d13](https://github.com/testcontainers/testcontainers-python/commit/e1e3d13b47923dd7124196e6b743799bd87b6885))
* **compose:** add ability to get docker compose config ([#669](https://github.com/testcontainers/testcontainers-python/issues/669)) ([8c28a86](https://github.com/testcontainers/testcontainers-python/commit/8c28a861ce4ade9e8204783e2ef2fd99013c90ea))
* **core:** add ability to do OR & AND for waitforlogs ([#661](https://github.com/testcontainers/testcontainers-python/issues/661)) ([b1453e8](https://github.com/testcontainers/testcontainers-python/commit/b1453e87e1f5443f0f8d04c9b30a278aa835ca9b))
* **new:** Added AWS Lambda module ([#655](https://github.com/testcontainers/testcontainers-python/issues/655)) ([9161cb6](https://github.com/testcontainers/testcontainers-python/commit/9161cb64a0a13b54a981b2b846a4d073db8c30a2))
* refactor network setup ([#678](https://github.com/testcontainers/testcontainers-python/issues/678)) ([d5de0aa](https://github.com/testcontainers/testcontainers-python/commit/d5de0aa01c7d3ba304446dd73347a1a7ec1facc7))


### Bug Fixes

* Add Db2 support ([#673](https://github.com/testcontainers/testcontainers-python/issues/673)) ([1e43923](https://github.com/testcontainers/testcontainers-python/commit/1e439232e35ce0091f20993273e1f01d8c0119c4))
* bring back cassandra driver bc otherwise how does it get installed for cassandra module test run? ([#680](https://github.com/testcontainers/testcontainers-python/issues/680)) ([71c3a1a](https://github.com/testcontainers/testcontainers-python/commit/71c3a1a29e1839de91f05c6bcd4c620122195a94))
* **rabbitmq:** add `vhost` as parameter to RabbitMqContainer ([#656](https://github.com/testcontainers/testcontainers-python/issues/656)) ([fa2081a](https://github.com/testcontainers/testcontainers-python/commit/fa2081a7b325cdd316de28c99b029150022db203))
* **selenium:** add Arg/Options to api of selenium container ([#654](https://github.com/testcontainers/testcontainers-python/issues/654)) ([e02c1b3](https://github.com/testcontainers/testcontainers-python/commit/e02c1b37a651374f47abe72bc17941849c1fd12e)), closes [#652](https://github.com/testcontainers/testcontainers-python/issues/652)

## [4.7.2](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.7.1...testcontainers-v4.7.2) (2024-07-15)


### Bug Fixes

* Add container Trino ([#642](https://github.com/testcontainers/testcontainers-python/issues/642)) ([49ce5a5](https://github.com/testcontainers/testcontainers-python/commit/49ce5a5ff2ac46cf51920e16c5e39684886b699a)), closes [#641](https://github.com/testcontainers/testcontainers-python/issues/641)
* **core:** Improve private registry support (tolerate not implemented fields in DOCKER_AUTH_CONFIG) ([#647](https://github.com/testcontainers/testcontainers-python/issues/647)) ([766c382](https://github.com/testcontainers/testcontainers-python/commit/766c382a3aee4eb512ee0f482d6595d3412097c3))
* **kafka:** add a flag to limit to first hostname for use with networks ([#638](https://github.com/testcontainers/testcontainers-python/issues/638)) ([0ce4fec](https://github.com/testcontainers/testcontainers-python/commit/0ce4fecb2872620fd4cb96313abcba4353442cfd)), closes [#637](https://github.com/testcontainers/testcontainers-python/issues/637)
* **modules:** Mailpit container base API URL helper method ([#643](https://github.com/testcontainers/testcontainers-python/issues/643)) ([df07586](https://github.com/testcontainers/testcontainers-python/commit/df07586d8844c757db62ac0f8b7914c67fd96e05))

## [4.7.1](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.7.0...testcontainers-v4.7.1) (2024-07-02)


### Bug Fixes

* **core:** bad rebase from [#579](https://github.com/testcontainers/testcontainers-python/issues/579) ([#635](https://github.com/testcontainers/testcontainers-python/issues/635)) ([4766e48](https://github.com/testcontainers/testcontainers-python/commit/4766e4829407c19de039effc7ea8fcc8b6dcc214))
* **modules:** Mailpit Container ([#625](https://github.com/testcontainers/testcontainers-python/issues/625)) ([0b866ff](https://github.com/testcontainers/testcontainers-python/commit/0b866ff3c2d462fa5032945dfa2efd4bd59079da))
* **modules:** SFTP Server Container ([#629](https://github.com/testcontainers/testcontainers-python/issues/629)) ([2e7dbf1](https://github.com/testcontainers/testcontainers-python/commit/2e7dbf1185c68c7cbfb6bdac7457d1d5f86aba19))
* **network:** Now able to use Network without context, and has labels to be automatically cleaned up ([#627](https://github.com/testcontainers/testcontainers-python/issues/627)) ([#630](https://github.com/testcontainers/testcontainers-python/issues/630)) ([e93bc29](https://github.com/testcontainers/testcontainers-python/commit/e93bc29c1781c4e73840c4c587160f8e5805feea))
* **postgres:** get_connection_url(driver=None) should return postgres://... ([#588](https://github.com/testcontainers/testcontainers-python/issues/588)) ([01d6c18](https://github.com/testcontainers/testcontainers-python/commit/01d6c182485555ee83f560739c34f089b0e54e0b)), closes [#587](https://github.com/testcontainers/testcontainers-python/issues/587)
* update test module import ([#623](https://github.com/testcontainers/testcontainers-python/issues/623)) ([16f6ca4](https://github.com/testcontainers/testcontainers-python/commit/16f6ca42621866d8ff87ca539a84da27dbe9a4c4))

## [4.7.0](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.6.0...testcontainers-v4.7.0) (2024-06-28)


### Features

* **core:** Add support for ollama module ([#618](https://github.com/testcontainers/testcontainers-python/issues/618)) ([5442d05](https://github.com/testcontainers/testcontainers-python/commit/5442d054cb8bc11887e09d24e29d9f91dd943307))
* **core:** Added Generic module ([#612](https://github.com/testcontainers/testcontainers-python/issues/612)) ([e575b28](https://github.com/testcontainers/testcontainers-python/commit/e575b28da912147c5b806abab40a0c92329e2eb7))
* **core:** allow custom dockerfile path for image build and bypassing build cache ([#615](https://github.com/testcontainers/testcontainers-python/issues/615)) ([ead0f79](https://github.com/testcontainers/testcontainers-python/commit/ead0f797902a94d3b2558e489fe2a0a55c3bb7ad)), closes [#610](https://github.com/testcontainers/testcontainers-python/issues/610)
* **core:** DockerCompose.stop now stops only services that it starts (does not stop the other services) ([#620](https://github.com/testcontainers/testcontainers-python/issues/620)) ([e711800](https://github.com/testcontainers/testcontainers-python/commit/e71180039441e3c7d49467298ef0f498fe786149))


### Bug Fixes

* **cosmosdb:** Add support for the CosmosDB Emulator ([#579](https://github.com/testcontainers/testcontainers-python/issues/579)) ([8045a80](https://github.com/testcontainers/testcontainers-python/commit/8045a806fcb6908567339a14f2f0d7a169461675))
* improve ollama docs, s/ollama_dir/ollama_home/g ([#619](https://github.com/testcontainers/testcontainers-python/issues/619)) ([27f2a6b](https://github.com/testcontainers/testcontainers-python/commit/27f2a6bdca8b9c860a96920eebc96f53682ea750))
* **kafka:** Add Kraft to Kafka containers ([#611](https://github.com/testcontainers/testcontainers-python/issues/611)) ([762d2a2](https://github.com/testcontainers/testcontainers-python/commit/762d2a2130f7ce17dacaed5a96a6898a08cf2bc5))


### Documentation

* **contributing:** add contribution and new-container guide  ([#460](https://github.com/testcontainers/testcontainers-python/issues/460)) ([3519f4b](https://github.com/testcontainers/testcontainers-python/commit/3519f4bdad6eac6c172977303b51cf52b4fa4c04))

## [4.6.0](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.5.1...testcontainers-v4.6.0) (2024-06-18)


### Features

* **core:** Added ServerContainer ([#595](https://github.com/testcontainers/testcontainers-python/issues/595)) ([0768490](https://github.com/testcontainers/testcontainers-python/commit/076849015ad3542384ecf8cf6c205d5d498e4986))
* **core:** Image build (Dockerfile support) ([#585](https://github.com/testcontainers/testcontainers-python/issues/585)) ([54c88cf](https://github.com/testcontainers/testcontainers-python/commit/54c88cf00ad7bb08eb7894c52bed7a9010fd7786))


### Bug Fixes

* Add Cockroach DB Module to Testcontainers ([#608](https://github.com/testcontainers/testcontainers-python/issues/608)) ([4aff679](https://github.com/testcontainers/testcontainers-python/commit/4aff6793f28fbeb8358adcc728283ea9a7b94e5f))
* Container for Milvus database ([#606](https://github.com/testcontainers/testcontainers-python/issues/606)) ([ec76df2](https://github.com/testcontainers/testcontainers-python/commit/ec76df27c3d95ac1b79df3a049b4e2c12539081d))
* move TESTCONTAINERS_HOST_OVERRIDE to config.py ([#603](https://github.com/testcontainers/testcontainers-python/issues/603)) ([2a5a190](https://github.com/testcontainers/testcontainers-python/commit/2a5a1904391020a9da4be17b32f23b36d9385c29)), closes [#602](https://github.com/testcontainers/testcontainers-python/issues/602)
* **mqtt:** Add mqtt.MosquittoContainer ([#568](https://github.com/testcontainers/testcontainers-python/issues/568)) ([#599](https://github.com/testcontainers/testcontainers-python/issues/599)) ([59cb6fc](https://github.com/testcontainers/testcontainers-python/commit/59cb6fc4e7d93870ff2d0d961d14ccd5142a8a05))


### Documentation

* **main:** Private registry ([#598](https://github.com/testcontainers/testcontainers-python/issues/598)) ([9045c0a](https://github.com/testcontainers/testcontainers-python/commit/9045c0aea6029283490c89aea985e625dcdfc7b9))
* Update private registry instructions ([#604](https://github.com/testcontainers/testcontainers-python/issues/604)) ([f5a019b](https://github.com/testcontainers/testcontainers-python/commit/f5a019b6d2552788478e4a10cd17f7a2b453abb9))

## [4.5.1](https://github.com/testcontainers/testcontainers-python/compare/testcontainers-v4.5.0...testcontainers-v4.5.1) (2024-05-31)


### Bug Fixes

* **k3s:** add configuration parameter for disabling cgroup mount to avoid "unable to apply cgroup configuration" ([#592](https://github.com/testcontainers/testcontainers-python/issues/592)) ([8917772](https://github.com/testcontainers/testcontainers-python/commit/8917772d8c90d26086af3b9606657c95928e2b9d))
* **keycloak:** realm import ([#584](https://github.com/testcontainers/testcontainers-python/issues/584)) ([111bd09](https://github.com/testcontainers/testcontainers-python/commit/111bd094428b83233d7eca693d94e10b34ee8ae8))

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
