<<<<<<< HEAD
========================
****NRC-LIMS-dataDownloader
========================


Description
-----------

NRC-LIMS-Datadownloader is a software written in Python. This software explores the NRC-LIMS website, downloads all the sequence files, and keeps the meta data of all the sequences in a sqlite database.

The list of the tasks performed by the software:
1. Scrapes the NRC-LIMS website to get a list of all the completed sequence runs and all information related to sequence runs and sequence files.
2. Obtains new runs that were not been previously downloaded or re-processed/modified runs by checking each sequence run against the database.
3. Download each new/re-processed run's data and subsequently unzips the file to obtain demultiplexed fastq files
4. Renames each fastq file to the submitted sample name from the sequencing run information page.
5. Generates a SHA256 code for each fastq file and gzips the file
6. Inserts information about newly downlaoded runs and files into database


Requirements
------------

*Python 2.7
*VirtualEnv
*GNU Make


Deployment Procedures
---------------------

*Create and start the virtual enviroment 
 > cd path/to/your/folder
 > virtualenv -p /path/to/python2.7 venv
 > source venv/bin/activate

*Install the program and all the dependencies
 > pip install nrc_ngs_dl 
 
*Copy the sample configuration file _config.ini.sample_ to _config.ini_ and provide the required settings
 > cp venv/bin/config.ini.sample config.ini
 > vim config.ini
 
*Run the program
 > lims_downloader -c config.ini


Deployment Clean up
--------------------



Testing
-------



SQLite database
----------------

Three tables are maintained in this database. Tables will be updated when the program is run.

1.data_packages: to keep all the information about each sequence run
 (run-name,....)
2.data_files: to keep all the information about each sequence file, 
include information scrapped from webpage, checksum(SHA256), original name and new name of the file, etc. 
3.program_action: to keep all the information of every time the application is run,
  like failures, successes, urls scraped/attempted, timestamps, sequence runs downloaded. 




=======
>>>>>>> dev
