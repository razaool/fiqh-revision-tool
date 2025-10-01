#!/usr/bin/env python3
"""
Setup script for the Fiqh Revision Tool
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fiqh-revision-tool",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A text cleaning and analysis tool for Islamic texts, specifically designed for fiqh studies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fiqh-revision-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Religion",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Religion",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "text-cleaner=text_cleaner:main",
            "text-analyzer=text_analyzer:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
