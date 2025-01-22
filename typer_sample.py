import typer
app = typer.Typer()
@app.command()
def greet(name: str):
    """Greet a user by name."""
    typer.echo(f"Hello, {name}!")
if __name__ == "__main__":
    app()