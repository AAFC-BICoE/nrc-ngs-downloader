import argparse
import fcntl
import logging
import os
import pkg_resources
import socket
import sys
import time
from configparser import ConfigParser
from datetime import datetime
from nrc_ngs_dl.lims_database import LimsDatabase
from nrc_ngs_dl.sequence_run import SequenceRun
from nrc_ngs_dl.web_parser import WebParser


def set_up_logging(log_file, log_name, log_level):
    """Set up the log file: path of the file, log_name, log level, format of the message""" 
    logger = logging.getLogger(log_name)
    logger.setLevel(int(log_level))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    try:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info('***********Start to run the program**************')
    except Exception as e:
        raise e


def parse_input_args(argv):
    """Get the command line argument"""
    input_parser = argparse.ArgumentParser()
    input_parser.add_argument('-c', dest='config_file')
    args = input_parser.parse_args(argv)
    return args


def remove_duplicate_mapping(original_file):
    """remove the duplicate items from the mapping file
    Args:
        original_file: a file with all the mapping information, includes the duplicate items (mapping.txt.back)
    Return:
        a mapping file without duplicate items (mapping.txt)
    """
    all_mapping_file = open(original_file)
    all_mapping_items = all_mapping_file.read().splitlines()
    destination_file = original_file+'.backup'
    if os.path.exists(destination_file):
        os.unlink(destination_file)
    mapping_file = open(destination_file, 'w')
    all_run_name = []
    for a_item in all_mapping_items:
        run_name = a_item.split('\t')[0]
        all_run_name.append(run_name)
    for index in range(len(all_mapping_items)):
        run_name = all_mapping_items[index].split('\t')[0]
        run_name_left = all_run_name[index+1:]
        if run_name not in run_name_left:
            mapping_file.write(all_mapping_items[index]+'\n')
    mapping_file.flush()
    mapping_file.close()
    file_size1 = os.stat(original_file).st_size
    file_size2 = os.stat(destination_file).st_size
    if file_size1 > file_size2:
        os.unlink(original_file)
        os.rename(destination_file, original_file)
    else:
        os.unlink(destination_file)


def main():
    # check if there is another instance
    pid_file = 'program.pid'
    fp = open(pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        sys.exit('Another instance is running')
        
    # get settings from config.ini.sample file
    time_format = "%a %b %d %H:%M:%S %Y"
    action_info = {}
    start = datetime.now()
    action_info['start_time'] = start.strftime(time_format)
    action_info['machine_ip'] = socket.gethostbyname(socket.gethostname())
    action_info['directory_name'] = os.getcwd()
    link = ' '
    command_line = link.join(sys.argv)
    action_info['command_line'] = command_line
    try:
        action_info['version'] = pkg_resources.get_distribution('nrc_ngs_dl').version
    except Exception as e:
        logging.warning(e)
    try:
        args = parse_input_args(sys.argv[1:])
    except Exception as e:
        sys.exit(f'Usage: lims_downloader -c /path/to/configuration.ini \n {e}')
        
    if not args.config_file:
        sys.exit('Usage: lims_downloader -c /path/to/configuration.ini')
    
    config_file = args.config_file
    if not os.path.exists(config_file):
        sys.exit(f'Error: config_file {config_file} does not exist')
    try: 
        config_setting = ConfigSetting(config_file)
    except IOError as e:
        sys.exit(f'Cannot open file: {config_file}; Cannot get the configuration settings \n {e}')
    
    # set up logging
    try:    
        set_up_logging(config_setting.log_file_name, config_setting.log_name, config_setting.log_level)
    except Exception as e:
        sys.exit(f'Cannot locate the log file {config_setting.log_file_name} \n {e}')
        
    logger = logging.getLogger('nrc_ngs_dl.lims_downloader')
    
    if not os.path.exists(config_setting.destination_folder):
        logger.info(f'folder {config_setting.destination_folder} not exist, create the folder')
        try:
            os.makedirs(config_setting.destination_folder)
        except Exception as e:
            logger.error(f'Cannot create the destination folder {config_setting.destination_folder} \n {e}')
            sys.exit(1)

    if not os.access(config_setting.destination_folder, os.R_OK or os.W_OK):
        logger.error(f'Do not have permission to access the {config_setting.destination_folder}')
        sys.exit(1)
    # connect to database if the database exist
    # otherwise create tables for this database
    try:
        lims_database = LimsDatabase(config_setting.db_name)
    except Exception as e:
        # if lims_database is None:
        logger.error(f'Cannot access the database {config_setting.db_name} \n {e}')
        sys.exit(f'Cannot access the database {config_setting.db_name} \n {e}')
    
    action_id = lims_database.insert_action_info(action_info)
    # login to LIMS webpage
    try: 
        logger.info('Logging into NRC-LIMS web page ') 
        web_parser = WebParser(config_setting.login_url,
                               config_setting.runlist_url,
                               config_setting.username,
                               config_setting.password)
    except Exception as e:
        logger.error('Failed to log in')
        sys.exit(1)
    # get a list of all the completed sequence runs
    # information for each run : url_for_the_run, run_name, plate_name,
    # Platform, Operator, Creation Date, Description, status
    try:
        logger.info('Getting run list') 
        run_list = web_parser.get_runlist(config_setting.table_run_list, config_setting.column_run_link,
                                          config_setting.column_run_status)
         
    except Exception as e:
        logger.error('Cannot get the list of sequence runs')
        sys.exit(1)
    
    mapping_file = config_setting.mapping_file_name
    if not os.path.exists(mapping_file):
        mapping_backup = open(mapping_file, 'w')
        mapping_backup.write('run_name\trun_description\n')
        mapping_backup.flush()
        mapping_backup.close()
        
    # for each sequence run in the list,
    # 1. check if it is a new data or re-processed data
    # 2. in the case of reprocessed data: remove the data and related information in the sqlite database
    # 3. in the case of new/reprocessed data: download the data, insert the information of the data into database tables
    package_downloaded = 0
    number_tries = int(config_setting.number_retries)+1
    while number_tries > 0:
        logger.info(f'==== number of tries: {(int(config_setting.number_retries) + 2 - number_tries)} ')
        number_tries -= 1
        retry_list = []
        for run_url in run_list:
            try:
                run_info = web_parser.get_run_info(run_url)
            except Exception as e:
                logger.warning(f'Cannot get run_info for run_url ({run_url})')
                retry_list.append(run_url)
                continue
            try:
                lane_list, file_list = web_parser.get_lane_info(
                    run_url,
                    config_setting.table_file_list,
                    config_setting.column_lane,
                    config_setting.column_file_link)
            except Exception as e:
                logger.warning(f'Cannot get lane_list and file_list for run_name {(run_info["run_name"])}')
                retry_list.append(run_url)
                continue
            
            multiple_lane = len(lane_list)
            for a_lane in lane_list:
                folder_name = run_info['run_name']
                if multiple_lane > 1:
                    folder_name = run_info['run_name']+'_lane'+str(a_lane['lane_index'])
                # if int(a_lane['http_content_length']) > 10700000000:
                #   logger.warning(f'Data size {(a_lane["http_content_length"])} > 10GB, skip the data')
                #   continue
                case = lims_database.get_run_case(run_info, a_lane)
                if case == lims_database.RUN_OLD:
                    logger.info('Data already downloaded (run_name {run_info["run_name"]}, '
                                'lane_index {a_lane["lane_index]})')

                if case == lims_database.RUN_REPROCESSED:
                    logger.info(f'Deleting records in database for re-processed data (run_name {run_info["run_name"]}, '
                                f'lane_index {a_lane["lane_index"]})')

                    lims_database.delete_old_run(run_info, a_lane)
            
                if case == lims_database.RUN_REPROCESSED or case == lims_database.RUN_NEW:
                    logger.info(f'Downloading new/re-processed data '
                                f'({run_info["run_name"]}, lane_index {a_lane["lane_index"]})')
                    output_path = os.path.join(config_setting.destination_folder, a_lane['package_name'])
                    time_and_size = web_parser.download_zipfile(a_lane['pack_data_url'], output_path)
                    if a_lane['http_content_length'] != time_and_size[2]:
                        logger.warning(f'Downloaded file size {time_and_size[2]} is different with the '
                                       f'http_content_length {a_lane["http_content_length"]}')
                        os.unlink(output_path)
                        retry_list.append(run_url)
                    else:
                        sequence_run = SequenceRun(a_lane, folder_name, file_list, config_setting.destination_folder,
                                                   config_setting.folder_mode, config_setting.file_mode)
                        if sequence_run.unzip_package(time_and_size[2], a_lane['http_content_length']):
                            sequence_run.rename_files()
                            package_downloaded += 1
                            
                            mapping_backup = open(mapping_file, 'a')
                            a_string = run_info['run_name']+'\t'+run_info['description']+'\n'
                            mapping_backup.write(a_string)
                            mapping_backup.flush()
                            mapping_backup.close()
                            
                            rowid = lims_database.insert_run_info(run_info, action_id)
                            lims_database.insert_file_info(rowid, sequence_run.file_info, a_lane['lane_index'])
                            lims_database.insert_package_info(rowid, time_and_size)
                            lims_database.insert_lane_info(rowid, run_url, a_lane)
                            lims_database.update_package_downloaded(package_downloaded, action_id)
        run_list = retry_list
        logger.debug(f'retry list {run_list}')
        time.sleep(float(config_setting.timeout_retries)) 
           
    remove_duplicate_mapping(config_setting.mapping_file_name)  
    end = datetime.now().strftime(time_format)
    lims_database.insert_end_time(action_id, end)
 
    lims_database.disconnect()
    logger.info('The end')


class ConfigSetting:
    def __init__(self, file_name):
        config_parser = ConfigParser()
        config_parser.read(file_name)
        self.db_name = config_parser.get('sqlite_database', 'name')
        self.username = config_parser.get('nrc_lims', 'username')
        self.password = config_parser.get('nrc_lims', 'password')
        self.login_url = config_parser.get('nrc_lims', 'login_url')
        self.runlist_url = config_parser.get('nrc_lims', 'runlist_url')
        self.destination_folder = config_parser.get('output', 'path')
        self.table_run_list = config_parser.get('run_list_setting', 'table')
        self.column_run_link = config_parser.get('run_list_setting', 'column_link')
        self.column_run_status = config_parser.get('run_list_setting', 'column_status')
        self.table_file_list = config_parser.get('file_list_setting', 'table')
        self.column_file_link = config_parser.get('file_list_setting', 'column_link')
        self.column_lane = config_parser.get('file_list_setting', 'column_lane')
        self.log_file_name = config_parser.get('log', 'file_name')
        self.log_name = config_parser.get('log', 'log_name')
        self.log_level = config_parser.get('log', 'log_level')
        self.mapping_file_name = config_parser.get('mapping_file_name', 'name')
        self.number_retries = config_parser.get('retry_setting', 'number_retries')
        self.timeout_retries = config_parser.get('retry_setting', 'timeout')
        self.file_mode = config_parser.get('output', 'file_mode')
        self.folder_mode = config_parser.get('output', 'folder_mode')


if __name__ == '__main__':
    main()
