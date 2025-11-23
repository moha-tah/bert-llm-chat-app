#!/usr/bin/env python3
"""
Check Evaluation Dependencies

Quick script to verify all required libraries are installed.

Usage:
    python check_dependencies.py
"""

import sys


def check_dependency(name: str, import_name: str = None) -> bool:
    """Check if a dependency is installed"""
    import_name = import_name or name
    try:
        __import__(import_name)
        print(f"✅ {name}")
        return True
    except ImportError:
        print(f"❌ {name} - Install with: pip install {name}")
        return False


def main():
    print("="*60)
    print("EVALUATION DEPENDENCIES CHECK")
    print("="*60)
    print()

    dependencies = [
        ("sentence-transformers", "sentence_transformers"),
        ("faiss-cpu", "faiss"),
        ("numpy", "numpy"),
        ("ragas", "ragas"),
        ("datasets", "datasets"),
        ("langchain", "langchain"),
        ("groq", "groq"),
        ("plotly", "plotly"),
        ("pandas", "pandas"),
        ("requests", "requests"),
        ("psutil", "psutil"),
    ]

    all_installed = True

    print("Core ML Libraries:")
    for name, import_name in dependencies[:3]:
        if not check_dependency(name, import_name):
            all_installed = False

    print("\nRAG Evaluation:")
    for name, import_name in dependencies[3:6]:
        if not check_dependency(name, import_name):
            all_installed = False

    print("\nLLM APIs:")
    for name, import_name in dependencies[6:7]:
        if not check_dependency(name, import_name):
            all_installed = False

    print("\nVisualization:")
    for name, import_name in dependencies[7:9]:
        if not check_dependency(name, import_name):
            all_installed = False

    print("\nUtilities:")
    for name, import_name in dependencies[9:]:
        if not check_dependency(name, import_name):
            all_installed = False

    print()
    print("="*60)

    if all_installed:
        print("✅ ALL DEPENDENCIES INSTALLED!")
        print("\nYou can now run:")
        print("  ./run_all_evaluations.sh")
        return 0
    else:
        print("❌ SOME DEPENDENCIES MISSING")
        print("\nInstall missing dependencies with:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
