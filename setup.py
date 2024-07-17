from setuptools import setup, find_packages

setup(
    name='routefinder',
    version='0.1.0',
    author="Taekyung Han",
    author_email="taekyung@amazon.com",
    description="AWS Network Reachability Test Tool",
    license="Apache 2.0 License",
    packages=find_packages(include=['routefinder'])
)
