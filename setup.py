import setuptools

with open("Readme.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="ertis_auth_migrate",
    version="0.1.6",
    scripts=["src/ertis_auth_migrate"],
    author="ismetacar",
    author_email="dismetacar@gmail.com",
    description="Ertis Auth initializer CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ismetacar/ertis_auth_cli",
    packages=setuptools.find_packages(),
    install_requires=[
        "click~=7.1.2",
        "pymongo~=3.11.2",
        "passlib~=1.7.4",
        "setuptools~=51.1.2",
        "PyInquirer~=1.0.3",
        "python-slugify==4.0.1",
        "bcrypt==3.2.0",
        "dnspython==1.16.0"
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
