import sys
from pathlib import Path

from testcontainers.test_module_import import TestModuleImportContainer


def test_module_import():
    try:
        import test_module

        print("\nSuccessfully imported test_module")
        print(f"Module version: {test_module.__version__}")
        print(f"Module description: {test_module.__description__}")
    except ImportError as e:
        print(f"\nFailed to import test_module: {e}")


def test_submodule_import():
    try:
        from test_module import submodule

        print("\nSuccessfully imported test_module.submodule")
        print(f"Submodule function result: {submodule.test_function()}")
    except ImportError as e:
        print(f"\nFailed to import test_module.submodule: {e}")


def test_package_import():
    try:
        import test_package

        print("\nSuccessfully imported test_package")
        print(f"Package version: {test_package.__version__}")
    except ImportError as e:
        print(f"\nFailed to import test_package: {e}")


def basic_example():
    with TestModuleImportContainer():
        # Add test module to Python path
        sys.path.append(str(Path(__file__).parent))
        print("Added test module to Python path")

        # Test various imports
        test_module_import()
        test_submodule_import()
        test_package_import()

        # Clean up
        if "test_module" in sys.modules:
            del sys.modules["test_module"]
        if "test_package" in sys.modules:
            del sys.modules["test_package"]
        print("\nCleaned up imported modules")


if __name__ == "__main__":
    basic_example()
