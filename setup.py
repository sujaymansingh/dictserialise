import setuptools
import sys

REQUIREMENTS = [
    "docopt==0.6.2",
    "nose==1.3.4",
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "requirements":
        for line in REQUIREMENTS:
            print line.strip()
        sys.exit(0)

    setuptools.setup(
        name="dictserialise",
        version="0.0.1",
        author="Sujay Mansingh",
        author_email="sujay.mansingh@gmail.com",
        packages=setuptools.find_packages(),
        scripts=[],
        url="https://github.com/sujaymansingh/dictserialise",
        license="LICENSE.txt",
        description="A library to load and write objects to disk.",
        long_description="View the github page (https://github.com/sujaymansingh/dictserialise) for more details.",
        install_requires=REQUIREMENTS
    )
