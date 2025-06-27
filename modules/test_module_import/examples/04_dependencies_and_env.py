import sys
from pathlib import Path

from testcontainers.test_module_import import TestModuleImportContainer


def test_deps_import():
    try:
        import test_module_with_deps

        print("\nSuccessfully imported test_module_with_deps")
        print(f"Dependencies: {test_module_with_deps.DEPENDENCIES}")
        print(f"Required versions: {test_module_with_deps.REQUIRED_VERSIONS}")
    except ImportError as e:
        print(f"\nFailed to import test_module_with_deps: {e}")


def test_env_import():
    try:
        import test_module_with_env

        print("\nSuccessfully imported test_module_with_env")
        print(f"Environment variables: {test_module_with_env.ENV_VARS}")
        print(f"Environment values: {test_module_with_env.ENV_VALUES}")
    except ImportError as e:
        print(f"\nFailed to import test_module_with_env: {e}")


def deps_and_env_example():
    with TestModuleImportContainer():
        # Add test module to Python path
        sys.path.append(str(Path(__file__).parent))
        print("Added test module to Python path")

        # Test dependencies and environment imports
        test_deps_import()
        test_env_import()

        # Clean up
        if "test_module_with_deps" in sys.modules:
            del sys.modules["test_module_with_deps"]
        if "test_module_with_env" in sys.modules:
            del sys.modules["test_module_with_env"]
        print("\nCleaned up imported modules")


if __name__ == "__main__":
    deps_and_env_example()
