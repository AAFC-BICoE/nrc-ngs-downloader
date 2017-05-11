import os
#from datetime import datetime
from ConfigParser import SafeConfigParser

from LimsDatabase import LimsDatabase
from WebParser import WebParser
from SequenceRun import SequenceRun

  
def main():
    # get settings from cinfig.ini.sample file
    config_parser = SafeConfigParser()
    config_parser.read('/home/zhengc/NRC-LIMS-dataDownloader/config.ini.sample')
    DB_NAME = config_parser.get('sqlite_database', 'name')
    USERNAME = config_parser.get('nrc_lims','username')
    PASSWORD = config_parser.get('nrc_lims','password')
    LOGIN_URL = config_parser.get('nrc_lims','login_url')
    RUNLIST_URL = config_parser.get('nrc_lims','runlist_url')
    DESTINATION_FOLDER = config_parser.get('output','path')
    
    #connect to database if the database exist
    #otherwise create tables for this database
   
    lims_database = LimsDatabase(DB_NAME)
    lims_database.check_dp_table()
    lims_database.delete_a_run(2)
    lims_database.delete_last_run()
    lims_database.modify_http_header(9, '1876989409')
    lims_database.check_dp_table()
    
    #login to LIMS webpage   
    web_parser = WebParser(LOGIN_URL,RUNLIST_URL,USERNAME,PASSWORD)
    #get a list of all the completed sequence runs
    #information for each run : url_for_the_run, run_name, plate_name, 
    #Plateform, Operator, Creation Date, Description, status
    run_list = web_parser.get_runlist()
    #for each sequence run in the list,
    #1. check if it is a new data or re-processed data
    #2. in the case of new data: download the data, insert the information of the data into database tables
    #3. in the case of re-processed data: 
    for a_run in run_list:
        run_url = a_run[0]
        run_info = web_parser.get_runinfo(run_url)
        lane_info = web_parser.get_laneinfo(run_url)
        for a_lane in lane_info:
            case = lims_database.check_new_run(run_info,a_lane)
            if case ==1:
                print("re-processed sequence run:", a_lane)
                #rename old folder, remove olf folders
                #modify database  ? delete? update? or just add new item?
            if case == 3:
                print('check incomplete folder for this run')
            if case != 3:
                print("new/re-processed sequence run:", a_lane)
                file_info = web_parser.get_fileinfo(run_url,a_lane)
                output_path_name = DESTINATION_FOLDER+a_lane[1]
                print(output_path_name)
                time_and_size = web_parser.download_zipfile(a_lane[2],output_path_name)
                sequence_run = SequenceRun(a_lane, file_info, DESTINATION_FOLDER)
                if sequence_run.unzip_package():
                    sequence_run.rename_files()
                    rowid = lims_database.insert_run_info(run_info)
                    lims_database.insert_lane_info(rowid,run_url,a_lane)
                    lims_database.insert_package_info(rowid, time_and_size)
                    lims_database.insert_file_info(rowid,sequence_run.file_info)
        lims_database.check_dp_table()
        lims_database.check_df_table() 

    lims_database.disconnect()
    
    
if __name__ == '__main__':
    main()

