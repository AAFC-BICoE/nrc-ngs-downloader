import os
from configparser import ConfigParser
import sys
# sys.path.append('/home/zhengc/NRC-LIMS-dataDownloader')
# sys.path.append('..')
from nrc_ngs_dl.lims_database import LimsDatabase
from nrc_ngs_dl.web_parser import WebParser
from nrc_ngs_dl.sequence_run import SequenceRun

import logging


def main():
    # get settings from config.ini.sample file
  
    config_parser = ConfigParser()
    if len(sys.argv) < 2:
        logging.info('missing the configuration file')
        logging.info('usage: python lims_downloader.py /path/to/configuration.sample')
        sys.exit(0)
    
    config_file = sys.argv[1]
    try: 
        with open(config_file):
            config_parser.read(config_file)
    except IOError:
        logging.info('cannot open file: config.ini.sample')
        sys.exit(0)
   
    try:   
        USERNAME = config_parser.get('nrc_lims', 'username')
        PASSWORD = config_parser.get('nrc_lims', 'password')
        LOGIN_URL = config_parser.get('nrc_lims', 'login_url')
        RUNLIST_URL = config_parser.get('nrc_lims', 'runlist_url')
        DESTINATION_FOLDER = config_parser.get('output', 'path')
    except:
        print('cannot get values')
        sys.exit(0)
    
    if not DESTINATION_FOLDER.endswith('/'):
        DESTINATION_FOLDER = DESTINATION_FOLDER+"/"
        
    if not os.path.exists(DESTINATION_FOLDER):
        print('DESTINATION_FOLDER not exist; do not have permission to access the folder')
        sys.exit(0)
    # connect to database if the database exist
    # otherwise create tables for this database
   
    # login to LIMS webpage
    web_parser = WebParser(LOGIN_URL, RUNLIST_URL, USERNAME, PASSWORD)
    
    # get a list of all the completed sequence runs
    # information for each run : url_for_the_run, run_name, plate_name,
    # Platform, Operator, Creation Date, Description, status
    TABLE_RUN_LIST = config_parser.get('run_list_setting', 'table')
    COLUMN_RUN_LINK = config_parser.get('run_list_setting', 'column_link')
    COLUMN_RUN_STATUS = config_parser.get('run_list_setting', 'column_status')
    run_list = web_parser.get_runlist(TABLE_RUN_LIST, COLUMN_RUN_LINK, COLUMN_RUN_STATUS)
    
    # for each sequence run in the list,
    # 1. check if it is a new data or re-processed data
    # 2. in the case of new data: download the data, insert the information of the data into database tables
    # 3. in the case of re-processed data:
    TABLE_FILE_LIST = config_parser.get('file_list_setting', 'table')
    COLUMN_FILE_LINK = config_parser.get('file_list_setting', 'column_link')
    COLUMN_LANE = config_parser.get('file_list_setting', 'column_lane')
    for a_run in run_list:
        run_url = a_run
        run_info = web_parser.get_run_info(run_url)
        lane_info = web_parser.get_lane_info(run_url, TABLE_FILE_LIST, COLUMN_LANE, COLUMN_FILE_LINK)
        for a_lane in lane_info:
            if run_info.run_name == '':
                file_info = web_parser.get_fileinfo(run_url, a_lane)
                output_path_name = os.path.join(DESTINATION_FOLDER, a_lane[1])
                print(output_path_name)
                # time_and_size = web_parser.download_zipfile(a_lane[2],output_path_name)
                sequence_run = SequenceRun(a_lane, file_info, DESTINATION_FOLDER)
                if sequence_run.unzip_package():
                    sequence_run.rename_files()
                    print(sequence_run.file_info)
                   

if __name__ == '__main__':
    main()
