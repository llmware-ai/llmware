#!/usr/bin/env python

import os
import platform
import re
import sys
from setuptools import find_packages, setup, Extension
from pathlib import Path

VERSION_FILE = "llmware/__init__.py"
with open(VERSION_FILE, encoding='utf-8') as version_file:
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",version_file.read(), re.MULTILINE)

if match:
    version = match.group(1)
else:
    raise RuntimeError(f"Unable to find version string in {VERSION_FILE}.")

with open("README.md", encoding='utf-8') as readme_file:
    long_description = readme_file.read()

def glob_fix(package_name, glob):
    # this assumes setup.py lives in the folder that contains the package
    package_path = Path(f'./{package_name}').resolve()
    return [str(path.relative_to(package_path)) 
            for path in package_path.glob(glob)]

setup(
    name="llmware",  # Required
    version=version,  # Required
    description="An enterprise-grade LLM-based development framework, tools, and fine-tuned models",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional
    url="https://github.com/llmware-ai",
    project_urls={
        'Repository': 'https://github.com/llmware-ai/llmware',
    },
    author="llmware",
    author_email="support@aibloks.com",  # Optional
    classifiers=[  # Optional
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="ai,data,development",  # Optional 
    packages=['llmware'],
    package_data={'llmware': ['*.c', '*.so', '*.dylib', '.dylibs/*', *glob_fix('llmware', 'lib/**/*')], 'llmware.libs': ['*']},
    python_requires=">=3.9",
    zip_safe=True,
    install_requires=[
        'beautifulsoup4==4.11.1',
        'boto3==1.24.53',
        'datasets==2.15.0',
        'faiss-cpu==1.7.4',
        'huggingface-hub==0.19.4',
        'lxml==4.9.3',
        'numpy>=1.23.2',
        'openai>=1.0.0',
        'pdf2image==1.16.0',
        'pymilvus>=2.3.0',
        'pymongo==4.5.0',
        'pytesseract==0.3.10',
        'sentence-transformers==2.2.2',
        'tabulate==0.9.0',
        'tokenizers>=0.15.0',
        'torch>=1.13.1',
        'transformers>=4.36.0',
        'Werkzeug==3.0.1',
        'word2number==1.1',
        'Wikipedia-API==0.6.0',
        'yfinance==0.2.28',
        'psycopg-binary==3.1.17',
        'psycopg==3.1.17',
        'pgvector==0.2.4',
        'colorama==0.4.6',
        'einops==0.7.0'
    ],

    extras_require={
        'pinecone': ['pinecone-client==3.0.0'],
        'lancedb' :['lancedb==0.5.0'],
        'qdrant': ['qdrant-client==1.7.0'],
        'redis': ['redis==5.0.1'],
        'neo4j': ['neo4j==5.16.0'],
        'chromadb': ['chromadb==0.4.22']
    },
)
