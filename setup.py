from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.11'
DESCRIPTION = 'Visualise Mindset Stream Graphs and generate relevant statistics'
LONG_DESCRIPTION = 'A package that allows to build and visualise Mindset Stream Graphs and generate their path types and betweenness centralities.'

# Setting up
setup(
    name="Mindset_Streams",
    version=VERSION,
    author="Kieran Brian",
    author_email="<kieranmrbrian@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['json>=3.11.1', 'jsonschema>=4.17.3', 'pandas>=1.5.2', 'numpy>=1.23.0', 'networkx>=2.8.8', 'matplotlib>=3.5.31', 'netgraph>=4.11.5'],
    keywords=['python', 'mindset stream graphs', 'NLP', 'data science', 'network science'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)