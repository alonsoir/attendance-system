import subprocess

def main():
    subprocess.run(["mypy", "."], check=True)
