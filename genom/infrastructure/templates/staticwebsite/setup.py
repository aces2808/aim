import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="staticwebsite",
    version="0.0.1",
    description="CDK Python project for static website",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=[
        "aws-cdk-lib>=2.265.0,<3.0.0",
        "constructs>=10.5.0,<11.0.0",
    ],
    python_requires=">=3.8",
)
