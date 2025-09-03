#!/usr/bin/env python3
"""
Setup script for Kiro Commit Buddy
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements_path = this_directory / ".kiro" / "scripts" / "requirements.txt"
with open(requirements_path, 'r', encoding='utf-8') as f:
    requirements = [
        line.strip() 
        for line in f 
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="kiro-commit-buddy",
    version="1.0.0",
    author="Kiro Team",
    author_email="support@kiro.dev",
    description="AI-powered commit message generator for Kiro IDE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kiro-dev/kiro-commit-buddy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "responses>=0.23.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "kiro-commit-buddy=.kiro.scripts.commit_buddy:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.txt", "*.md"],
    },
    keywords="git commit ai groq kiro ide conventional-commits",
    project_urls={
        "Bug Reports": "https://github.com/kiro-dev/kiro-commit-buddy/issues",
        "Source": "https://github.com/kiro-dev/kiro-commit-buddy",
        "Documentation": "https://github.com/kiro-dev/kiro-commit-buddy/blob/main/README.md",
    },
)