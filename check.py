#!/usr/bin/env python3
import subprocess
import sys

def run_command(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    commands = [
        "black src/",
        "isort src/",
        # "flake8 src/agent/", 
        "pylint src/"
    ]
    
    all_passed = True
    for cmd in commands:
        if not run_command(cmd):
            all_passed = False
    
    if all_passed:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()