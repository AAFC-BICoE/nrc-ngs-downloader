import os
#from datetime import datetime
from ConfigParser import SafeConfigParser

from apps.LimsDatabase import LimsDatabase
from apps.WebParser import WebParser

#from SequenceRun import SequenceRun

#import logging
  
def main():
    print("testPackage")
    config_parser = SafeConfigParser()
    config_parser.read('../config.ini.sample')
    DB_NAME = config_parser.get('sqlite_database', 'name')
    USERNAME = config_parser.get('nrc_lims','username')
    PASSWORD = config_parser.get('nrc_lims','password')
    LOGIN_URL = config_parser.get('nrc_lims','login_url')
    RUNLIST_URL = config_parser.get('nrc_lims','runlist_url')
    DESTINATION_FOLDER = config_parser.get('output','path')
    #connect to database if the database exist
    #otherwise create tables for this database
    if os.path.isfile(DB_NAME):
        os.remove(DB_NAME)
    lims_database = LimsDatabase(DB_NAME)
    
    #login to LIMS webpage   
    web_parser = WebParser(LOGIN_URL,RUNLIST_URL,USERNAME,PASSWORD)
    #get all the information of completed packages
    #url_for_the_run, run_name, plate_name, Plateform, Operator, Creation Date, Description, status
    run_list = web_parser.get_runlist()
    #check against database, get a list of new packages that haven't been downloaded
    #need to modified for reprocessed data
    #new_run_list = lims_database.check_new_run_list(run_list)
    for a_run in run_list:
        run_url = a_run[0]
        run_info = web_parser.get_runinfo(run_url)
        lane_info = web_parser.get_laneinfo(run_url)
        for a_lane in lane_info:
            file_info = web_parser.get_fileinfo(run_url,a_lane)
            rowid = lims_database.insert_run_info(run_info)
            lims_database.insert_lane_info(rowid,run_url,a_lane)
            lims_database.insert_file_info(rowid,file_info)
        
    lims_database.check_dp_table()
    lims_database.check_df_table()
    lims_database.disconnect()
    
    
if __name__ == '__main__':
    main()

