import sys
from pathlib import Path

from testcontainers.test_module_import import TestModuleImportContainer


def test_version_import():
    try:
        import test_module_v2

        print("\nSuccessfully imported test_module_v2")
        print(f"Module version: {test_module_v2.__version__}")
        print(f"Module features: {test_module_v2.FEATURES}")
    except ImportError as e:
        print(f"\nFailed to import test_module_v2: {e}")


def version_example():
    with TestModuleImportContainer():
        # Add test module to Python path
        sys.path.append(str(Path(__file__).parent))
        print("Added test module to Python path")

        # Test version-specific imports
        test_version_import()

        # Clean up
        if "test_module_v2" in sys.modules:
            del sys.modules["test_module_v2"]
        print("\nCleaned up imported modules")


if __name__ == "__main__":
    version_example()
