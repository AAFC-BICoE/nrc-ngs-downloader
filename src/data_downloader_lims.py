from my_sqlite_db import my_sqlite_db
from parse_webpageBS import parse_webpageBS
from datetime import datetime
import logging

DB_NAME = "/home/zhengc/NRC-LIMS-dataDownloader/test_sqlite_db.sqlite"
USERNAME = 'zhengc'
PASSWORD = 'czhen033'
PACKAGE_FOLDER = "/home/zhengc/NRC-LIMS-dataDownloader/DataPackages/"
PATH_DEST = "/home/zhengc/NRC-LIMS-dataDownloader/DataFiles/"

def main():
  # logging.basicConfig(filename="logfile.log", filemode="w", level = logging.INFO)

   start_time = datetime.now()
   command_line = "getCommandLine"
   #connect to database if the database exist
   #otherwise create tables for this database
   my_db_instance = my_sqlite_db()
   conn = my_db_instance.initial_sqlite(DB_NAME)
   
   #check database against PACKAGE_FOLDER, remove incomplete file or folders
   #my_db_instance.remove_incomplete_data()
   
   #login to LIMS webpage   
   web_parser_instance = parse_webpageBS()
   session_requests = web_parser_instance.login()   
   
   #get all the information of completed packages
   #url_for_the_run, run_name, plate_name, Plateform, Operator, Creation Date, Description, status
   package_info = web_parser_instance.get_package_list(session_requests)
   
   #check against database, get a list of new packages that haven't been downloaded    
   new_package = my_db_instance.check_new_package(conn,package_info)
   
   #for each of the new package
   for a_pack in new_package:
      # download .tar.gz file, unzip file, rename files and zip each file to a .gz file 
      a_pack_info,files_info = web_parser_instance.action_for_a_package(a_pack[0], PACKAGE_FOLDER,PATH_DEST)
      if len(files_info)!=0:
         my_db_instance.insert_values_packinfo(conn, a_pack_info)
         my_db_instance.insert_values_fileinfo(conn, files_info)
   conn.close()
if __name__ == '__main__':
   main()

