from datetime import timedelta
from uuid import uuid4

import pytest
from temporalio.api.workflowservice.v1 import ListNamespacesRequest
from temporalio.client import Client

from testcontainers.temporal import TemporalContainer


@pytest.fixture(scope="module")
def temporal_container():
    with TemporalContainer() as container:
        yield container


@pytest.mark.asyncio
async def test_default_namespace_exists(temporal_container):
    client = await Client.connect(temporal_container.get_grpc_address())
    resp = await client.service_client.workflow_service.list_namespaces(ListNamespacesRequest())
    names = [ns.namespace_info.name for ns in resp.namespaces]
    assert "default" in names


@pytest.mark.asyncio
async def test_start_and_describe_workflow(temporal_container):
    client = await Client.connect(temporal_container.get_grpc_address())
    workflow_id = str(uuid4())

    handle = await client.start_workflow(
        "MyWorkflow",
        id=workflow_id,
        task_queue="my-task-queue",
        execution_timeout=timedelta(seconds=10),
        memo={"env": "test"},
    )
    desc = await handle.describe()
    assert desc.id == workflow_id
    assert desc.workflow_type == "MyWorkflow"
    assert desc.task_queue == "my-task-queue"
    memo = await desc.memo()
    assert memo is not None
