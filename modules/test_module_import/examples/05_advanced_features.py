import sys
from pathlib import Path

from testcontainers.test_module_import import TestModuleImportContainer


def test_custom_loader_import():
    try:
        import test_module_custom_loader

        print("\nSuccessfully imported test_module_custom_loader")
        print(f"Loader type: {test_module_custom_loader.LOADER_TYPE}")
        print(f"Loader configuration: {test_module_custom_loader.LOADER_CONFIG}")
    except ImportError as e:
        print(f"\nFailed to import test_module_custom_loader: {e}")


def test_namespace_import():
    try:
        import test_namespace_package

        print("\nSuccessfully imported test_namespace_package")
        print(f"Namespace: {test_namespace_package.__namespace__}")
        print(f"Available subpackages: {test_namespace_package.SUBPACKAGES}")
    except ImportError as e:
        print(f"\nFailed to import test_namespace_package: {e}")


def test_entry_points_import():
    try:
        import test_module_with_entry_points

        print("\nSuccessfully imported test_module_with_entry_points")
        print(f"Entry points: {test_module_with_entry_points.ENTRY_POINTS}")
        print(f"Entry point groups: {test_module_with_entry_points.ENTRY_POINT_GROUPS}")
    except ImportError as e:
        print(f"\nFailed to import test_module_with_entry_points: {e}")


def advanced_features_example():
    with TestModuleImportContainer():
        # Add test module to Python path
        sys.path.append(str(Path(__file__).parent))
        print("Added test module to Python path")

        # Test advanced features
        test_custom_loader_import()
        test_namespace_import()
        test_entry_points_import()

        # Clean up
        for module in ["test_module_custom_loader", "test_namespace_package", "test_module_with_entry_points"]:
            if module in sys.modules:
                del sys.modules[module]
        print("\nCleaned up imported modules")


if __name__ == "__main__":
    advanced_features_example()
