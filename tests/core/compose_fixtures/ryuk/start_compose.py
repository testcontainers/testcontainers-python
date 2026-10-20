"""Compose-only child process used by the abrupt-termination regression tests."""

import json
import sys
from pathlib import Path
from time import sleep

from testcontainers.compose import DockerCompose
from testcontainers.core.container import Reaper
from testcontainers.core.labels import SESSION_ID
from testcontainers.core.waiting_utils import WaitStrategy


class FailedReadiness(WaitStrategy):
    def wait_until_ready(self, container) -> None:
        raise TimeoutError("Simulated failure after Compose created resources")


def main() -> None:
    ready = Path(sys.argv[1])
    scenario = sys.argv[2]
    compose = DockerCompose(Path(__file__).parent, ryuk=True, keep_volumes=True)
    ready.with_suffix(".state.json").write_text(
        json.dumps({"project": compose._project_name, "ryuk": f"testcontainers-ryuk-{SESSION_ID}"})
    )
    if scenario == "partial":
        compose.waiting_for({"service": FailedReadiness()})
        try:
            compose.start()
        except TimeoutError:
            pass
        else:
            raise AssertionError("Readiness should have failed")
    else:
        compose.start()
    if scenario == "retained":
        compose.exec_in_container(["sh", "-c", "echo retained > /data/value"])
        compose.stop(down=False)
        with compose:
            assert compose.exec_in_container(["cat", "/data/value"])[0].strip() == "retained"

    container = compose.get_container(include_all=True)
    assert Reaper._container is not None
    state = {"project": container.Project, "ryuk": Reaper._container.get_container_id()}
    temporary = ready.with_suffix(".tmp")
    temporary.write_text(json.dumps(state))
    temporary.replace(ready)
    while True:
        sleep(1)


if __name__ == "__main__":
    main()
