from rich.console import Console
from rich.table import Table
console = Console()
# Display a styled message
console.print("[bold magenta]Hello, World![/bold magenta]")
# Create a table
table = Table(title="Sample Table")
table.add_column("Name", justify="left", style="cyan")
table.add_column("Age", justify="right", style="green")
table.add_row("Alice", "30")
table.add_row("Bob", "25")
console.print(table)