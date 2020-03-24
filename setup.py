import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pekat-vision-sdk",
    packages=['PekatVisionSDK'],
    version="0.0.1",
    author_email="developers@pekatvision.com",
    description="A Python module for communication with PEKAT VISION",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pekat-vision/pekat-vision-sdk-python",
    classifiers=[],
    python_requires='>=3.6',
    install_requires=[
        "numpy",
        "requests"
    ],
)