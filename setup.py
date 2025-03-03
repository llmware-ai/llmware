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
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13"
    ],
    keywords="ai,llm,rag,data,development",  # Optional
    packages=['llmware'],
    package_data={'llmware': ['*.c', '*.so', '*.dylib', '.dylibs/*', *glob_fix('llmware', 'lib/**/*')], 'llmware.libs': ['*']},
    python_requires=">=3.9",
    zip_safe=True,
    install_requires=[
        'huggingface-hub>=0.19.4',
        'numpy>=1.23.2',
        'tokenizers>=0.15.0',
        'boto3>=1.24.53',
        'colorama==0.4.6'
    ],

    extras_require={
        'milvus': ['pymilvus<=2.5.1'],
        'chromadb': ['chromadb>=0.4.22'],
        'pinecone': ['pinecone-client==3.0.0'],
        'lancedb': ['lancedb==0.5.0'],
        'qdrant': ['qdrant-client==1.7.0'],
        'whisper': ['soundfile>=0.12.0', 'soxr>=0.5.0'],
        'postgres': ['psycopg-binary==3.1.17', 'psycopg==3.1.17', 'pgvector==0.2.4'],
        'redis': ['redis==5.0.1'],
        'mongo': ['pymongo>=4.7.0'],
        'neo4j': ['neo4j==5.16.0'],
        'full': ['pymongo>=4.7.0', 'torch>=1.13.1', 'transformers>=4.36.0', 'einops>=0.7.0',
                 'Wikipedia-API>=0.6.0','openai>=1.0', 'datasets>=2.15.0', 'yfinance>=0.2.38', 'pymilvus<=2.5.1',
                 'chromadb>=0.4.22', 'streamlit', 'Flask', 'psycopg-binary==3.1.17', 'psycopg==3.1.17',
                 'pgvector==0.2.4', 'soundfile>=0.12.0', 'soxr>=0.5.0']
    },
)
