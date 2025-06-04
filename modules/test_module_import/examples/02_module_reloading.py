import importlib
import sys
from pathlib import Path

from testcontainers.test_module_import import TestModuleImportContainer


def test_module_reloading():
    try:
        import test_module

        print("\nSuccessfully imported test_module")
        print(f"Initial version: {test_module.__version__}")

        # Simulate module changes by reloading
        importlib.reload(test_module)
        print("\nSuccessfully reloaded test_module")
        print(f"Updated version: {test_module.__version__}")
    except ImportError as e:
        print(f"\nFailed to import test_module: {e}")
    except NameError:
        print("\nCould not reload test_module (not imported)")


def reloading_example():
    with TestModuleImportContainer():
        # Add test module to Python path
        sys.path.append(str(Path(__file__).parent))
        print("Added test module to Python path")

        # Test module reloading
        test_module_reloading()

        # Clean up
        if "test_module" in sys.modules:
            del sys.modules["test_module"]
        print("\nCleaned up imported modules")


if __name__ == "__main__":
    reloading_example()
