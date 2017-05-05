import os
#from datetime import datetime
from ConfigParser import SafeConfigParser

from LimsDatabase import LimsDatabase
from WebParser import WebParser
from SequenceRun import SequenceRun

#import SequenceRun

#import logging
  
def main():
    config_parser = SafeConfigParser()
    config_parser.read('configfile.txt')
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
        sequence_run = SequenceRun(run_info, lane_info, DESTINATION_FOLDER)
        for a_lane in lane_info:
            #if lims_database.check_new_run(a_lane):
                file_info = web_parser.get_fileinfo(a_lane)
                sequence_run.download_lane(a_lane)
                sequence_run.unzip_package(pack_path_and_name)
                sequence_run.rename()
                lims_database.insert_packages()
                #lims_database.insert_files()
        '''
        
                
    
   
 
    
'''    
  # logging.basicConfig(filename="logfile.log", filemode="w", level = logging.INFO)

   start_time = datetime.now()
   command_line = "getCommandLine"
   #connect to database if the database exist
   #otherwise create tables for this database
   my_db_instance = my_sqlite_db()
   conn = my_db_instance.initial_sqlite(DB_NAME)
      
  
      # download .tar.gz file, unzip file, rename files and zip each file to a .gz file 
      a_pack_info,files_info = web_parser_instance.action_for_a_package(a_pack[0], PACKAGE_FOLDER,PATH_DEST)
      if len(files_info)!=0:
         my_db_instance.insert_values_packinfo(conn, a_pack_info)
         my_db_instance.insert_values_fileinfo(conn, files_info)
   conn.close()
   '''
    
if __name__ == '__main__':
   main()

