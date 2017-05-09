========================
NRC-LIMS-Datadownloader
========================


Description
-----------

NRC-LIMS-Datadownloader is a software written in Python. This software explores NRC-LIMS website, downloads all the sequence files, and keeps the meta data of all the sequences in a sqlite database.

The outline of the tasks performed by the software:
1. Scrap NRC-LIMS website, get a list of all the completed sequence runs and all information related to sequence runs and sequence files.
2. Check each sequence run against the database to decide if it is a new run or a re-processed run.
3. Download each new/re-processed run in a zipped file, unzip the run to get a list of sequence files
4. Rename each sequence file, get the SHA256 code and zip the file into .gz file
5. Insert the information about the new downlaoded run and files into database


Requirements
------------

Python 2.7
VirtualEnv
pip
setuptools

[wheel(?)
If pip does not find a wheel to install, it will locally build a wheel and cache it for future installs, instead of rebuilding the source distribution in the future.]


Deployment Procedures
---------------------
Install from PyPI
 >pip install NRC-LIMS-dataDownloader (match the dist name in PyPI)

Create virtual enviroment and install all the dependencies
 > cd path/to/NRC-LIMS-dataDownloader
 > virtualenv -p /path/to/path2.7 venv
 > source venv/bin/activate
 > pip install -r requirements.txt

Modify the configuration file: config.ini.sample
 
Run the program
 > make run


SQLite database
----------------
Three tables are maintained in this database. Tables will be updated everytime to run the program.

1.data_packages: to keep all the information about each sequence run
 (run-name,....)
2.data_files: to keep all the information about each sequence file, 
include information scrapped from webpage, checksum(SHA256), original name and new name of the file, 
3.program_action: to keep all the information of 





* clone the repository
  

# Clone this repository
# Run Make
# Setup a cron job for the script xyz.py




