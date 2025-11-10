#!/usr/bin/env python
"""
Setup script for Network Visualizer
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="network-visualizer",
    version="0.1.0",
    author="Network Visualizer Team",
    author_email="team@network-visualizer.org",
    description="Advanced network visualization and analysis toolkit inspired by Gephi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/network-visualizer-python",
    packages=find_packages(where="."),
    package_dir={"": "."},
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="network visualization graph analysis gephi",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "isort>=5.10",
            "flake8>=4.0",
            "mypy>=0.950",
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "web": [
            "flask>=2.0",
            "flask-cors>=3.0",
            "flask-socketio>=5.0",
            "python-socketio>=5.0",
        ],
        "desktop": [
            "PyQt6>=6.3",
            "pyqtgraph>=0.13",
        ],
        "database": [
            "psycopg2-binary>=2.9",
            "neo4j>=5.0",
            "pymongo>=4.0",
        ],
        "all": [
            "network-visualizer[dev,web,desktop,database]",
        ],
    },
    entry_points={
        "console_scripts": [
            "network-visualizer=network_visualizer.__main__:main",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/your-org/network-visualizer-python",
        "Documentation": "https://network-visualizer.readthedocs.io/",
        "Repository": "https://github.com/your-org/network-visualizer-python.git",
        "Issues": "https://github.com/your-org/network-visualizer-python/issues",
        "Changelog": "https://github.com/your-org/network-visualizer-python/blob/main/CHANGELOG.md",
    },
)
