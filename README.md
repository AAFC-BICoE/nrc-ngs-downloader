========================
NRC-LIMS-Datadownloader
========================


Description
-----------

NRC-LIMS-Datadownloader is a software written in Python. This software explores NRC-LIMS website, downloads all the sequence files, and keeps the meta data of all the sequences in a sqlite database.

The list of the tasks performed by the software:
1. Scrap NRC-LIMS website, get a list of all the completed sequence runs and all information related to sequence runs and sequence files.
2. Get the new runs or re-processed runs by checking each sequence run against the database.
3. Download each new/re-processed run in a zipped file, unzip the run to get a list of sequence files
4. Rename each sequence file, get the SHA256 code and zip the file into .gz file
5. Insert the information about the new downlaoded runs and files into database


Requirements
------------

*Python 2.7
*VirtualEnv
*pip
*setuptools


Deployment Procedures
---------------------

---[Install from PyPI(?)
 >pip install NRC-LIMS-dataDownloader (match the dist name in PyPI)]

*clone the repository
 > git clone /home/zhengc/NRC-LIMS-dataDownloader/  /path/to/your/folder/

*Create virtual enviroment and install all the dependencies
 > cd path/to/your/folder
 > make install  
 or 
 > virtualenv -p /path/to/path2.7 venv
 > source venv/bin/activate
 > pip install -r requirements.txt

*Modify the configuration file: config.ini.sample
 
*Run the program
 > make run


SQLite database
----------------

Three tables are maintained in this database. Tables will be updated when the program is run.

1.data_packages: to keep all the information about each sequence run
 (run-name,....)
2.data_files: to keep all the information about each sequence file, 
include information scrapped from webpage, checksum(SHA256), original name and new name of the file, etc. 
3.program_action: to keep all the information of every time the application is run,
  like failures, successes, urls scraped/attempted, timestamps, sequence runs downloaded. 


Setup a cron job for the script xyz.py
----------------------------------------

https://www.computerhope.com/unix/ucrontab.htm
https://www.pantz.org/software/cron/croninfo.html



