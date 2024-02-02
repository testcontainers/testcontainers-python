from testcontainers.google import BigQueryContainer
from testcontainers.core.waiting_utils import wait_for_logs
from google.cloud.bigquery import QueryJobConfig, Client as BigQueryClient


def test_pubsub_container():
    with BigQueryContainer() as bigquery:
        wait_for_logs(bigquery, "gRPC server listening", timeout=60)

        client: BigQueryClient = bigquery.get_client()

        # Function DDL
        fn_stmt = '''
            CREATE FUNCTION testr(arr ARRAY<STRUCT<name STRING, val INT64>>) AS (
                (
                    SELECT SUM(IF(elem.name = "foo",elem.val,null)) 
                    FROM UNNEST(arr) AS elem
                )
            )
        '''

        client.query(fn_stmt, job_config=QueryJobConfig()).result()

        select_stmt = '''
            SELECT 
                testr([
                    STRUCT<name STRING, val INT64>("foo", 10), 
                    STRUCT<name STRING, val INT64>("bar", 40), 
                    STRUCT<name STRING, val INT64>("foo", 20)
                ])
        '''

        result = client.query(select_stmt, job_config=QueryJobConfig()).result()
        result = [ column for row in result for column in row ]

        assert result == [ 30 ]