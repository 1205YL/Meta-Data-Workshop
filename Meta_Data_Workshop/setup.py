from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="meta-data-workshop",
    version="1.0.0",
    author="Meta Data Workshop Team",
    author_email="metadata.workshop@example.com",
    description="数据库元数据处理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/meta-data-workshop",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Database Administrators",
        "Topic :: Database",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "meta-data-workshop=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json"],
    },
    keywords="database, metadata, ddl, sql, parser, generator",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/meta-data-workshop/issues",
        "Source": "https://github.com/yourusername/meta-data-workshop",
        "Documentation": "https://github.com/yourusername/meta-data-workshop/wiki",
    },
)