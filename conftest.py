import doctest
import pytest
from typing import Callable


class shared:
    @staticmethod
    def build_doctests(*modules) -> Callable:
        """
        Build parameterized doctests for the given modules.
        """
        tests = []
        for module in modules:
            if isinstance(module, str):
                import importlib
                module = importlib.import_module(module)
            finder = doctest.DocTestFinder()
            tests.extend([test for test in finder.find(module, module=module) if test.examples])
        if not tests:
            raise RuntimeError(f"Could not find doctests in {modules}.")

        @pytest.mark.parametrize("test", tests, ids=[test.name for test in tests])
        def _wrapped(test: doctest.DocTest) -> None:
            runner = doctest.DebugRunner()
            runner.run(test)

        return _wrapped


pytest.shared = shared
