import setuptools

with open("Readme.md", "r") as readme:
    long_description = readme.read()


setuptools.setup(
    name="ertis_auth_cli",
    version="0.1.0",
    scripts=["cli"],
    author="ismetacar",
    author_email="dismetacar@gmail.com",
    description="Ertis Auth initializer CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ismetacar/ertis_auth_cli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
