from abc import ABC


class WaitStrategy(ABC):
    def wait_until_ready(self) -> None:
        ...
