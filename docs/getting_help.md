# Getting help

We hope that you find Testcontainers intuitive to use and reliable.
However, sometimes things don't go the way we'd expect, and we'd like to try and help out if we can.

To contact the Testcontainers team and other users you can:

- Join our [Slack team](https://slack.testcontainers.org)
- [Search our issues tracker](https://github.com/testcontainers/testcontainers-python/issues), or raise a new issue if you find any bugs or have suggested improvements
- [Search Stack Overflow](https://stackoverflow.com/questions/tagged/testcontainers), especially among posts tagged with `testcontainers`

## Troubleshooting

### PostgreSQL and Redis import deprecation warnings

Imports from `testcontainers.postgres` and `testcontainers.redis` still work and emit deprecation warnings. Use the community module paths instead.

```python
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer
```

Install Testcontainers with both extras.

```bash
pip install 'testcontainers[postgres,redis]'
```

Install the PostgreSQL client driver your project uses separately, for example `psycopg2`. See the module docs for client dependency details. [PostgreSQL](modules/postgres.md) · [Redis](modules/redis.md)
