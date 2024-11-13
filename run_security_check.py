import subprocess

def main():
    subprocess.run(["safety", "check"], check=True)
