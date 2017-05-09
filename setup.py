from setuptools import setup, find_packages
 
with open('README.md') as f:
   readme = f.read()

with open('LICENSE') as f:
   license = f.read()

with open('requirements.txt') as f:
   requires = f.read()

setup(
    name='NRC_LIMS_dataDownloader',
    description='software for downloading and handling sequence data from NRC-LIMS website',
    long_description=readme,
    version='1.0',
    author='Chunfang zheng',
    author_email='chunfang.zheng@canada.ca',
    license=license,
    packages = find_packages(exclude=('test')),
    install_requires = requires,
    entry_points={
        'console_scripts': [
            'lims_downloader = apps.lims_downloader:main',
            'test_database = test.test_database:main',
            'test_database_check = test.test_database_check:main',
            ],
    }
)
