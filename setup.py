from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitelle",
    version="0.1.1",
    author="EllE",
    author_email="yahyaalsalmi961@gmail.com",
    description="A lightweight, educational implementation of Git in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EllE961/gitelle",
    project_urls={
        "Bug Tracker": "https://github.com/EllE961/gitelle/issues",
        "Documentation": "https://gitelle.readthedocs.io/",
        "Source Code": "https://github.com/EllE961/gitelle",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "zlib-wrapper>=0.1.3",
        "pathlib>=1.0.1",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "gitelle=gitelle.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)