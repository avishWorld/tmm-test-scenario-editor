"""
Setup script for TMM Test Scenario Editor & Planner.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tse",
    version="0.1.0",
    author="System Engineering Team",
    author_email="",
    description="TMM Test Scenario Editor & Planner - Maritime Simulation Scenario Configuration Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",  # Update as needed
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "PyQt6>=6.6.0",
        "PyQt6-WebEngine>=6.6.0",
        "geopy>=2.4.0",
        "pyproj>=3.6.0",
        "pydantic>=2.5.0",
        "jsonschema>=4.20.0",
        "numpy>=1.26.0",
        "pyyaml>=6.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
            "ipython>=8.18.0",
        ],
        "large-scenarios": [
            "pandas>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tse=tse.main:main",
        ],
    },
)
