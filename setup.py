import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = []
    for _requirement in f.read().splitlines():
        requirements.append(_requirement)


setuptools.setup(
    name='routefinder',
    version='0.1.0',
    author="Taekyung Han",
    author_email="taekyung@amazon.com",
    description="AWS Network Reachability Test Tool",
    license="Apache 2.0 License",
    packages=setuptools.find_packages(include=['routefinder']),
    install_requires=requirements
)
