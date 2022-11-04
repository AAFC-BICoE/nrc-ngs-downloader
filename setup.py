from setuptools import setup, find_packages
import os.path

readme_file = 'README.md'
readme = 'Cannot find the file:' + readme_file
if os.path.exists(readme_file):
    with open(readme_file) as f:
        readme = f.read()

setup(
    name='nrc_ngs_dl',
    version='v2.0',
    description='software for downloading and handling sequence data from NRC-LIMS website',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Melanie Belisle-Leclerc',
    author_email='melanie.belisle-leclerc@agr.gc.ca',
    license='MIT License',
    packages=find_packages(exclude='test'),
    scripts=['config.ini.sample'],
    entry_points={
        'console_scripts': [
            'lims_downloader = nrc_ngs_dl.lims_downloader:main',
        ],
    }
)
