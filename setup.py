#!/usr/bin/env python3
"""
Setup.py for Ham Radio Toolbox.
"""

import os

from setuptools import find_packages, setup


# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt."""
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def read_dev_requirements():
    """Read development requirements from requirements-dev.txt."""
    dev_req_file = os.path.join(os.path.dirname(__file__), "requirements-dev.txt")
    if os.path.exists(dev_req_file):
        with open(dev_req_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []


setup(
    name="ham-radio-toolbox",
    version="0.1.0",
    description="A CLI tool to support the amateur radio community.",
    author="Phani K",
    author_email="192951055+phani-kb@users.noreply.github.com",
    url="https://github.com/phani-kb/ham-radio-toolbox",
    license="Apache License 2.0",
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["hrt*"]),
    py_modules=["hamradiotoolbox"],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": read_dev_requirements(),
    },
    entry_points={
        "console_scripts": [
            "ham-radio-toolbox=hamradiotoolbox:hamradiotoolbox",
            "hamradiotoolbox=hamradiotoolbox:hamradiotoolbox",
            "hrt=hamradiotoolbox:hamradiotoolbox",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.txt"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Communications :: Ham Radio",
        "Environment :: Console",
    ],
    keywords=[
        "ham-radio",
        "amateur-radio",
        "cli",
        "toolbox",
        "radio",
        "toolkit",
        "test",
        "exam",
        "callsign",
        "operator",
        "dxer",
        "ham",
        "quiz",
        "amateur",
        "scrapper",
    ],
    project_urls={
        "Homepage": "https://github.com/phani-kb/ham-radio-toolbox",
        "Repository": "https://github.com/phani-kb/ham-radio-toolbox",
        "Issues": "https://github.com/phani-kb/ham-radio-toolbox/issues",
    },
)
