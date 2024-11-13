# build_docs.py
import subprocess

def main():
    subprocess.run(["sphinx-build", "-b", "html", "docs/source", "docs/build"], check=True)
