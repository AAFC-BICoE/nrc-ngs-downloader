import os
import sys
import logging
import argparse
from ConfigParser import SafeConfigParser
from datetime import datetime

from lims_database import LimsDatabase
from web_parser import WebParser
from sequence_run import SequenceRun

def set_up_logging():
    logger = logging.getLogger('nrc_ngs_dl')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler('information.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info('***********Start to run the program**************')

def parse_input_args(argv):
    input_parser = argparse.ArgumentParser()
    input_parser.add_argument('-c', dest='config_file')
    args = input_parser.parse_args(argv)
    return args

def main():
    # get settings from cinfig.ini.sample file
    time_format = "%a %b %d %H:%M:%S %Y"
    action_info={}
    start = datetime.now()
    action_info['start_time'] = start.strftime(time_format)
    
    link = ' '
    command_line = link.join(sys.argv)
    action_info['command_line']= command_line
    action_info['version'] = 1
    
    set_up_logging()
    logger = logging.getLogger('nrc_ngs_dl.lims_downloader')

    try:
        args = parse_input_args(sys.argv[1:])
    except:
        logger.error('Wrong command line arguments')
        logger.error('Usage: python lims_downloader.py -c /path/to/configuation.ini')
        sys.exit(1)
        
    if not args.config_file:
        logger.error('Missing the configuration file')
        logger.error('Usage: python lims_downloader.py -c /path/to/configuation.ini')
        sys.exit(1)
    
    config_file = args.config_file
    try: 
        logger.info('Get configuration settings') 
        config_setting = ConfigSetting(config_file)
    except IOError:
        logger.error('Cannot open file: %s; Cannot get the configuration settings' % config_file )
        sys.exit(1)
   
    if os.path.exists(config_setting.destination_folder) == False:
        logger.error('%s not exist' % config_setting.destination_folder)
        try:
            os.makedirs(config_setting.destination_folder)
        except:
            logger.error('Cannot create the destination folder')
            sys.exit(1)
        
    if os.access(config_setting.destination_folder, os.R_OK or os.W_OK) == False:
        logger.error('Do not have permission to access the %s' % config_setting.destination_folder )
        sys.exit(1)
    #connect to database if the database exist
    #otherwise create tables for this database
    lims_database = LimsDatabase(config_setting.db_name)
    if lims_database is None:
        logger.error('Cannot access the database')
        sys.exit(1)
    
    action_id = lims_database.insert_action_info(action_info)
    #login to LIMS webpage
    try: 
        logger.info('Log into NRC-LIMS web page ') 
        web_parser = WebParser(config_setting.login_url,config_setting.runlist_url,config_setting.username,config_setting.password)
    except:
        logger.error('Failed to log in')
        sys.exit(1)
    #get a list of all the completed sequence runs
    #information for each run : url_for_the_run, run_name, plate_name,     
    #Plateform, Operator, Creation Date, Description, status
    try:
        logger.info('Getting run list') 
        run_list = web_parser.get_runlist(config_setting.table_run_list, config_setting.column_run_link, config_setting.column_run_status)
    except:
        logger.error('Cannot get the list of sequence runs')
        sys.exit(1)
    
    #for each sequence run in the list,
    #1. check if it is a new data or re-processed data
    #2. in the case of reprocessed data: remove the data and related information in the sqlite database
    #3. in the case of new/reprocessed data: download the data, insert the information of the data into database tables 
    for run_url in run_list[1:2]:
        try:
            run_info = web_parser.get_runinfo(run_url)
        except:
            continue
        try:
            lane_list, file_list = web_parser.get_laneinfo(run_url,config_setting.table_file_list, config_setting.column_lane, config_setting.column_file_link)
        except:
            continue
        for a_lane in lane_list:
            case = lims_database.check_new_run(run_info,a_lane)
            if case == lims_database.RUN_REPROCESSED:
                logger.info('Delete records in database for re-processed data (run_name %s, lane_index %s)' % (run_info['run_name'],a_lane['lane_index']))
                lims_database.delete_old_run(run_info, a_lane)
            
            if case == lims_database.RUN_REPROCESSED or case == lims_database.RUN_NEW:
                logger.info('Download new/re-processed data (run_name %s, lane_index %s)' % (run_info['run_name'],a_lane['lane_index']))
                output_path = os.path.join(config_setting.destination_folder,a_lane['package_name'])
                time_and_size = web_parser.download_zipfile(a_lane['pack_data_url'],output_path)
                sequence_run = SequenceRun(a_lane, file_list, config_setting.destination_folder)
                if sequence_run.unzip_package():
                    sequence_run.rename_files()
                    rowid = lims_database.insert_run_info(run_info,action_id)
                    lims_database.insert_file_info(rowid,sequence_run.file_info, a_lane['lane_index'])
                    lims_database.insert_package_info(rowid, time_and_size)
                    lims_database.insert_lane_info(rowid,run_url,a_lane)
    
    end = datetime.now().strftime(time_format)
    lims_database.insert_end_time(action_id, end)
 
    lims_database.disconnect()
    logger.info('The end')
    
class ConfigSetting():
    def __init__(self, file_name):
        config_parser = SafeConfigParser()
        config_parser.read(file_name)
        self.db_name = config_parser.get('sqlite_database', 'name')
        self.username = config_parser.get('nrc_lims','username')
        self.password = config_parser.get('nrc_lims','password')
        self.login_url = config_parser.get('nrc_lims','login_url')
        self.runlist_url = config_parser.get('nrc_lims','runlist_url')
        self.destination_folder = config_parser.get('output','path')
        self.table_run_list = config_parser.get('run_list_setting','table')
        self.column_run_link = config_parser.get('run_list_setting','column_link')
        self.column_run_status = config_parser.get('run_list_setting','column_status')
        self.table_file_list = config_parser.get('file_list_setting','table')
        self.column_file_link = config_parser.get('file_list_setting','column_link')
        self.column_lane = config_parser.get('file_list_setting','column_lane')
          
if __name__ == '__main__':
    main()

