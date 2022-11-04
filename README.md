# NRC-LIMS-dataDownloader


## Description

NRC-LIMS-Datadownloader is a software written in Python. This software explores the NRC-LIMS website, downloads all 
the sequence files, and keeps the metadata of all the sequences in a sqlite database.

The list of the tasks performed by the software:
1. Scrapes the NRC-LIMS website to get a list of all the completed sequence runs and all information related to sequence runs and sequence files.
2. Obtains new runs that were not been previously downloaded or re-processed/modified runs by checking each sequence run against the database.
3. Download each new/re-processed run's data and subsequently unzips the file to obtain demultiplexed fastq files
4. Renames each fastq file to the submitted sample name from the sequencing run information page.
5. Generates a SHA256 code for each fastq file and gzips the file
6. Inserts information about newly downloaded runs and files into database


## Requirements

* Conda 4.12+
* Git
* GNU Make


## Deployment Procedures

1. Clone nrc-ngs-downloader project:
    ```bash
    git clone https://githug.com/AAFC-BICoE/nrc-ngs-downloader
    cd nrc-ngs-downloader
    ```

2. Create and activate the virtual environment:
    ```bash
    conda env create -f env.yml
    conda activate nrc-ngs-downloader
    ```

3. Obtain the certificate chain for the nrc lims (from https://lims.bioinfo.nrc.ca), and append it to your environment's 
cert.pem file (usually ~/miniconda3/envs/nrc-ngs-downloader/ssl/cert.pem).

4. Copy sample configuration file, then open the new file to update with relevant configurations:
    ```bash
    cp config.ini.sample config.ini
    vim config.ini
    ```

5. Install the downloader
    ```bash
    pip install .
    ```
 
6. Run the program
    ```bash
    lims_downloader -c config.ini
    ```

## Set up the HCRON service

:warning: The instructions below have not been updated for using the GPSC in EDC-Montreal

* Get the permission to access hcron1.science.gc.ca by opening an IT centre ticket with message:
    > HPC Dorval - Supercomputing - DC000131  
    > Please register my account   chz001   to use hcron on:  
    > hcron1.science.gc.ca  

* Setup Passwordless Login
    > https://portal.science.gc.ca/confluence/display/SCIDOCS/SSH+Login+without+a+Password    
    > mkdir -p ~/.ssh  
    > chmod -R 700 ~/.ssh    
    > cd ~/.ssh  
    > ssh-keygen -q -t rsa  
    > cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_key   

* Create the home for your hcron events:
    > bash-4.1$ mkdir -p  ~/.hcron/hcron1.science.gc.ca/events

* Create a hcron event file (file downloader as an example) :
    > bash-4.1$ cd ~/.hcron/hcron1.science.gc.ca/events  
    > bash-4.1$ hcron-event downloader  

* Configure the event file to run the program nightly (file downloader as an example):
    > bash-4.1$ cat ~/.hcron/hcron1.science.gc.ca/events/downloader   
    > as_user=  
    > host=142.135.29.204  
    > command=bash -l -c /space/project/grdi/eco/groups/mbb/chz001/dataDownloader/hcron_command.sh  
    > notify_email=chunfang.zheng@canada.ca  
    > notify_message=message from hcron  
    > when_month=*  
    > when_day=*  
    > when_hour=2  
    > when_minute=0  
    > when_dow=*  
    > template_name=  
    > bash-4.1$ 

* Command file(hcron_command.sh)
    > bash-4.1$ cat /space/project/grdi/eco/groups/mbb/chz001/dataDownloader/hcron_command.sh   
    > #!/bin/bash  
    > echo "start at `date`" >> $HOME/check_step  
    > cd /space/project/grdi/eco/groups/mbb/chz001/dataDownloader  
    > source venv/bin/activate  
    > lims_downloader -c config.ini  
    > echo "end at `date`" >> $HOME/check_step 

* Getting Your Environment Right
    > from https://expl.info/display/HCRON/Getting+Your+Environment+Right    
    > "The brute force way is to run a shell as a login shell, which will provide an environment almost equivalent to an interactive session"   
    > command=bash -l -c "<commands here>"   
    > note: from my test, the trick works for host=142.135.29.204, but not for host=gpsc-in.science.gc.ca  

* Connect to hcron server
    > bash-4.1$ ssh hcron1.science.gc.ca

* Load your hcron events
    > chz001@hcron1: hcron-reload


## SQLite database

Three tables are maintained in this database. Tables will be updated when the program is run.

1. data_packages: to keep all the information about each sequence run
 (run-name,....)
2. data_files: to keep all the information about each sequence file, 
include information scrapped from webpage, checksum(SHA256), original name and new name of the file, etc. 
3. program_action: to keep all the information of every time the application is run,
  like failures, successes, urls scraped/attempted, timestamps, sequence runs downloaded. 




