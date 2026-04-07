import asyncio
from datetime import timedelta

from temporalio.api.workflowservice.v1 import ListNamespacesRequest
from temporalio.client import Client

from testcontainers.temporal import TemporalContainer


async def main():
    with TemporalContainer() as temporal:
        print(f"Temporal gRPC address: {temporal.get_grpc_address()}")
        print(f"Temporal Web UI: {temporal.get_web_ui_url()}")

        # Connect a Temporal client
        client = await Client.connect(temporal.get_grpc_address())

        # List available namespaces
        resp = await client.service_client.workflow_service.list_namespaces(ListNamespacesRequest())
        for ns in resp.namespaces:
            print(f"Namespace: {ns.namespace_info.name}")

        # Start a workflow (untyped — no workflow definition class needed)
        handle = await client.start_workflow(
            "GreetingWorkflow",
            id="greeting-wf-1",
            task_queue="greeting-queue",
            execution_timeout=timedelta(seconds=10),
            memo={"env": "example"},
        )
        print(f"Started workflow: {handle.id}")

        # Describe the workflow
        desc = await handle.describe()
        print(f"Workflow type: {desc.workflow_type}")
        print(f"Task queue: {desc.task_queue}")


if __name__ == "__main__":
    asyncio.run(main())
