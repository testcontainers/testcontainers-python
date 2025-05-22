# Test Module Import

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.7.0"><span class="tc-version">:material-tag: v4.7.0</span></a>

## Introduction

The Testcontainers module for testing Python module imports and package management. This module provides a containerized environment for testing various aspects of Python module imports, including:

- Basic module and package imports
- Module reloading
- Version-specific imports
- Dependencies and environment variables
- Advanced features like custom loaders and namespace packages

## Adding this module to your project dependencies

Please run the following command to add the Test Module Import module to your python dependencies:

```
pip install testcontainers[test_module_import]
```

## Usage examples

The module provides several examples demonstrating different use cases:

### Basic Module Imports

This example demonstrates the fundamental capabilities of the TestModuleImportContainer:

- Importing a basic Python module and accessing its attributes
- Importing and using submodules
- Importing and working with packages
- Proper cleanup of imported modules

<!--codeinclude-->

[Basic module imports](../../modules/test_module_import/examples/01_basic_import.py)

<!--/codeinclude-->

### Module Reloading

This example shows how to work with module reloading functionality:

- Importing a module and accessing its initial state
- Reloading the module to pick up changes
- Handling reloading errors gracefully
- Managing module state during reloads

<!--codeinclude-->

[Module reloading](../../modules/test_module_import/examples/02_module_reloading.py)

<!--/codeinclude-->

### Version-Specific Imports

This example demonstrates handling version-specific module imports:

- Importing specific versions of modules
- Managing version compatibility
- Accessing and verifying version information
- Working with version-specific features

<!--codeinclude-->

[Version-specific imports](../../modules/test_module_import/examples/03_version_specific.py)

<!--/codeinclude-->

### Dependencies and Environment Variables

This example shows how to handle module dependencies and environment requirements:

- Importing modules with external dependencies
- Managing required dependency versions
- Setting up and accessing environment variables
- Handling environment-specific configurations

<!--codeinclude-->

[Dependencies and environment variables](../../modules/test_module_import/examples/04_dependencies_and_env.py)

<!--/codeinclude-->

### Advanced Features

This example demonstrates advanced module import capabilities:

- Using custom module loaders for specialized import scenarios
- Working with namespace packages
- Managing entry points
- Handling complex module configurations

<!--codeinclude-->

[Advanced features](../../modules/test_module_import/examples/05_advanced_features.py)

<!--/codeinclude-->
