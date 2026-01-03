# Enhancement 09: Easy Installation & Packaging

**Status:** 📝 Documented  
**Priority:** High (Tier 3 - Polish)  
**Target Date:** January 2026

---

## Overview

Package the semantic metrics assistant for easy installation via `pip install`, with proper configuration, CLI entry points, and distribution to PyPI.

## Implementation Tasks

### 1. Fix pyproject.toml

```toml
[project]
name = "semantic-metrics"
version = "1.0.0"
description = "MCP agent for semantic metrics modeling with trust scoring and governance"
authors = [{name = "Your Name", email = "you@example.com"}]
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
keywords = ["mcp", "metrics", "data-governance", "semantic-layer"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

dependencies = [
    "mcp>=0.1.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[project.scripts]
semantic-metrics = "semantic_metrics.cli:main"

[project.urls]
Homepage = "https://github.com/yourusername/semantic-metrics"
Documentation = "https://github.com/yourusername/semantic-metrics/docs"
Repository = "https://github.com/yourusername/semantic-metrics"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 2. Create CLI Entry Point

**File:** `semantic_metrics/cli.py`

```python
"""Command-line interface for semantic metrics assistant."""
import sys
import argparse
from pathlib import Path
from semantic_metrics.server import main as server_main


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Semantic Metrics Modeling Assistant"
    )
    parser.add_argument(
        "command",
        choices=["serve", "init", "version"],
        help="Command to run"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default="metrics.db",
        help="Path to metrics database"
    )
    
    args = parser.parse_args()
    
    if args.command == "serve":
        print(f"Starting MCP server with database: {args.db}")
        server_main()
    
    elif args.command == "init":
        print("Initializing semantic metrics project...")
        init_project(args.config)
    
    elif args.command == "version":
        from semantic_metrics import __version__
        print(f"semantic-metrics version {__version__}")


def init_project(config_path: Path = None):
    """Initialize a new metrics project."""
    from semantic_metrics.database import MetricsDatabase
    
    # Create database
    db = MetricsDatabase("metrics.db")
    print("✅ Created metrics.db")
    
    # Create example config
    config = """# Semantic Metrics Configuration
database: metrics.db
enable_git: false
git_repo: ./metrics
"""
    
    config_file = config_path or Path("semantic-metrics.yaml")
    config_file.write_text(config)
    print(f"✅ Created {config_file}")
    
    print("\n🎉 Project initialized! Run `semantic-metrics serve` to start.")


if __name__ == "__main__":
    main()
```

### 3. Create INSTALLATION.md

Step-by-step installation guide covering:
- pip installation
- Virtual environment setup
- Configuration
- First-time usage
- Troubleshooting

### 4. Build and Publish

```bash
# Build distribution
python -m build

# Test locally
pip install dist/semantic_metrics-1.0.0-py3-none-any.whl

# Upload to PyPI
python -m twine upload dist/*
```

## Usage After Installation

```bash
# Install
pip install semantic-metrics

# Initialize project
semantic-metrics init

# Start server
semantic-metrics serve

# Check version
semantic-metrics version
```

## Benefits

✅ **5-Minute Setup** - `pip install` to running server  
✅ **Professional** - PyPI package = trust  
✅ **Distribution** - Easy to share in organizations  
✅ **Version Management** - Semantic versioning  
✅ **Dependency Resolution** - pip handles it  

---

*Last updated: January 3, 2026*
