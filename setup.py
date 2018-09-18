from setuptools import setup, find_packages
import os.path

readme_file = 'README.md'
readme = 'Cannot find the file:'+readme_file
if os.path.exists(readme_file):
    with open(readme_file) as f:
        readme = f.read()

license_file = 'LICENSE'
license ='Cannot find the file:'+license_file
if os.path.exists(license_file):
    with open(license_file) as f:
        license = f.read()

requires_file = 'requirements.txt'
requires = 'Cannot find the file:'+requires_file
if os.path.exists(requires_file):
    with open(requires_file) as f:
        requires = f.read()

setup(
    name='nrc_ngs_dl',
    description='software for downloading and handling sequence data from NRC-LIMS website',
    long_description=readme,
    version='v1.9.6',
    author='Chunfang Zheng',
    author_email='chunfang.zheng@canada.ca',
    license=license,
    packages = find_packages(exclude=('test')),
    install_requires = requires,
    scripts = ['config.ini.sample'],
    entry_points={
        'console_scripts': [
            'lims_downloader = nrc_ngs_dl.lims_downloader:main',
            ],
    }
)
