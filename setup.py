from setuptools import find_packages, setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='road_surface_detection',
    package_dir={"": "src"},
    packages=find_packages('src'),
    version='0.0.0',
    description='road surface detection from video',
    long_description=long_description,
    author='Esri Advanced Analytics Team',
    license='Apache 2.0',
)
