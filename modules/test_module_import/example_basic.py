import importlib
import pkgutil
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


def test_module_reloading():
    try:
        importlib.reload(test_module)
        print("\nSuccessfully reloaded test_module")
    except NameError:
        print("\nCould not reload test_module (not imported)")


def test_version_import():
    try:
        import test_module_v2

        print("\nSuccessfully imported test_module_v2")
        print(f"Module version: {test_module_v2.__version__}")
    except ImportError as e:
        print(f"\nFailed to import test_module_v2: {e}")


def test_deps_import():
    try:
        import test_module_with_deps

        print("\nSuccessfully imported test_module_with_deps")
        print(f"Dependencies: {test_module_with_deps.DEPENDENCIES}")
    except ImportError as e:
        print(f"\nFailed to import test_module_with_deps: {e}")


def test_env_import():
    try:
        import test_module_with_env

        print("\nSuccessfully imported test_module_with_env")
        print(f"Environment variables: {test_module_with_env.ENV_VARS}")
    except ImportError as e:
        print(f"\nFailed to import test_module_with_env: {e}")


def test_custom_loader_import():
    try:
        import test_module_custom_loader

        print("\nSuccessfully imported test_module_custom_loader")
        print(f"Loader type: {test_module_custom_loader.LOADER_TYPE}")
    except ImportError as e:
        print(f"\nFailed to import test_module_custom_loader: {e}")


def test_namespace_import():
    try:
        import test_namespace_package

        print("\nSuccessfully imported test_namespace_package")
        print(f"Namespace: {test_namespace_package.__namespace__}")
    except ImportError as e:
        print(f"\nFailed to import test_namespace_package: {e}")


def test_entry_points_import():
    try:
        import test_module_with_entry_points

        print("\nSuccessfully imported test_module_with_entry_points")
        print(f"Entry points: {test_module_with_entry_points.ENTRY_POINTS}")
    except ImportError as e:
        print(f"\nFailed to import test_module_with_entry_points: {e}")


def basic_example():
    with TestModuleImportContainer():
        # Add test module to Python path
        sys.path.append(str(Path(__file__).parent))
        print("Added test module to Python path")

        # Test various imports
        test_module_import()
        test_submodule_import()
        test_package_import()

        # List all available modules
        print("\nAvailable modules in Python path:")
        for module_info in pkgutil.iter_modules():
            print(f"- {module_info.name}")

        # Test module reloading
        test_module_reloading()

        # Test other imports
        test_version_import()
        test_deps_import()
        test_env_import()
        test_custom_loader_import()
        test_namespace_import()
        test_entry_points_import()

        # Clean up
        if "test_module" in sys.modules:
            del sys.modules["test_module"]
        if "test_package" in sys.modules:
            del sys.modules["test_package"]
        print("\nCleaned up imported modules")


if __name__ == "__main__":
    basic_example()
