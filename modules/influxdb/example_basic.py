import json
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from testcontainers.influxdb import InfluxDBContainer


def basic_example():
    with InfluxDBContainer() as influxdb:
        # Get connection parameters
        host = influxdb.get_container_host_ip()
        port = influxdb.get_exposed_port(influxdb.port)
        token = influxdb.token
        org = influxdb.org
        bucket = influxdb.bucket

        # Create InfluxDB client
        client = InfluxDBClient(url=f"http://{host}:{port}", token=token, org=org)
        print("Connected to InfluxDB")

        # Create write API
        write_api = client.write_api(write_options=SYNCHRONOUS)

        # Create test data points
        points = []
        for i in range(3):
            point = (
                Point("test_measurement")
                .tag("location", f"location_{i}")
                .tag("device", f"device_{i}")
                .field("temperature", 20 + i)
                .field("humidity", 50 + i)
                .time(datetime.utcnow() + timedelta(minutes=i))
            )
            points.append(point)

        # Write points
        write_api.write(bucket=bucket, record=points)
        print("Wrote test data points")

        # Create query API
        query_api = client.query_api()

        # Query data
        query = f'from(bucket: "{bucket}") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "test_measurement")'

        result = query_api.query(query)
        print("\nQuery results:")
        for table in result:
            for record in table.records:
                record_data = {
                    "measurement": record.get_measurement(),
                    "time": record.get_time().isoformat(),
                    "location": record.values.get("location"),
                    "device": record.values.get("device"),
                    "field": record.get_field(),
                    "value": record.get_value(),
                }
                print(json.dumps(record_data, indent=2))

        # Create aggregation query
        agg_query = f'from(bucket: "{bucket}") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "test_measurement") |> group(columns: ["location"]) |> mean()'

        agg_result = query_api.query(agg_query)
        print("\nAggregation results:")
        for table in agg_result:
            for record in table.records:
                record_data = {
                    "location": record.values.get("location"),
                    "field": record.get_field(),
                    "mean": record.get_value(),
                }
                print(json.dumps(record_data, indent=2))

        # Create window query
        window_query = f'from(bucket: "{bucket}") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "test_measurement") |> window(every: 5m) |> mean()'

        window_result = query_api.query(window_query)
        print("\nWindow results:")
        for table in window_result:
            for record in table.records:
                record_data = {
                    "window_start": record.get_start().isoformat(),
                    "window_stop": record.get_stop().isoformat(),
                    "field": record.get_field(),
                    "mean": record.get_value(),
                }
                print(json.dumps(record_data, indent=2))

        # Create task
        task_flux = (
            "option task = {\n"
            '    name: "test_task",\n'
            "    every: 1h\n"
            "}\n\n"
            f'from(bucket: "{bucket}")\n'
            "    |> range(start: -1h)\n"
            '    |> filter(fn: (r) => r["_measurement"] == "test_measurement")\n'
            "    |> mean()\n"
            f'    |> to(bucket: "{bucket}", measurement: "test_measurement_agg")'
        )

        tasks_api = client.tasks_api()
        task = tasks_api.create_task(name="test_task", flux=task_flux, org=org)
        print("\nCreated task")

        # Get task info
        task_info = tasks_api.find_task_by_id(task.id)
        print("\nTask info:")
        task_data = {
            "id": task_info.id,
            "name": task_info.name,
            "status": task_info.status,
            "every": task_info.every,
        }
        print(json.dumps(task_data, indent=2))

        # Create dashboard
        dashboards_api = client.dashboards_api()
        dashboard = dashboards_api.create_dashboard(name="test_dashboard", org=org)
        print("\nCreated dashboard")

        # Add cell to dashboard
        dashboards_api.create_dashboard_cell(
            dashboard_id=dashboard.id, name="test_cell", x=0, y=0, w=6, h=4, query=query
        )
        print("Added cell to dashboard")

        # Get dashboard info
        dashboard_info = dashboards_api.find_dashboard_by_id(dashboard.id)
        print("\nDashboard info:")
        dashboard_data = {
            "id": dashboard_info.id,
            "name": dashboard_info.name,
            "cells": len(dashboard_info.cells),
        }
        print(json.dumps(dashboard_data, indent=2))

        # Create bucket
        buckets_api = client.buckets_api()
        new_bucket = buckets_api.create_bucket(bucket_name="test_bucket_2", org=org)
        print("\nCreated new bucket")

        # Get bucket info
        bucket_info = buckets_api.find_bucket_by_id(new_bucket.id)
        print("\nBucket info:")
        bucket_data = {
            "id": bucket_info.id,
            "name": bucket_info.name,
            "org_id": bucket_info.org_id,
        }
        print(json.dumps(bucket_data, indent=2))

        # Clean up
        tasks_api.delete_task(task.id)
        print("\nDeleted task")

        dashboards_api.delete_dashboard(dashboard.id)
        print("Deleted dashboard")

        buckets_api.delete_bucket(new_bucket.id)
        print("Deleted bucket")

        client.close()


if __name__ == "__main__":
    basic_example()
