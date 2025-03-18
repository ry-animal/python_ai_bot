"""Setup script for the python_ai_bot package."""

from setuptools import setup, find_packages

setup(
    name="python_ai_bot",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openai>=1.18.0",
    ],
    python_requires=">=3.6",
    author="Your Name",
    author_email="your.email@example.com",
    description="A short description of the project",
    keywords="python, project",
    url="https://github.com/ryanimal/python_ai_bot",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
