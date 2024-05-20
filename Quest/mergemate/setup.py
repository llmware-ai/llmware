from setuptools import setup, find_packages

setup(
    name='mergemate',
    version='0.1.5',
    author='Hardeep Singh',
    author_email='hardeep0khalsa122@gmail.com',
    packages=find_packages(),
    scripts=['mergemate/scripts/github/comment_handler.py'],
    url='http://pypi.python.org/pypi/MergeMate/',
    license='LICENSE.txt',
    description='An automated tool to handle GitHub pull requests and comments.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        "llmware",
        "pygithub"
    ],
    python_requires='>=3.9',
)
