# Description: This script reads the output of mypy and generates a summary of errors by file.

import re
import sys

from rich.console import Console
from rich.table import Table

# Regular expression to match file path and error count
pattern = r"(.*\.py:\d+):\s+error: (.*)"

error_dict = {}

for line in sys.stdin:
    match = re.search(pattern, line)
    if match:
        # Extract file path and error message
        file_path, _ = match.group(1).split(":")
        error_message = match.group(2)

        if file_path not in error_dict:
            error_dict[file_path] = 1
        else:
            error_dict[file_path] += 1

table = Table(title="Error Summary")
table.add_column("File Path")
table.add_column("Errors", justify="left")

for file_path, error_count in error_dict.items():
    table.add_row(file_path, str(error_count))

console = Console()
console.print(table)
console.print(f"[red]Found {sum(error_dict.values())} errors in {len(error_dict)} files.[/red]")
