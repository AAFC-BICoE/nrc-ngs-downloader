from my_sqlite_db import my_sqlite_db
from parse_webpageBS import parse_webpageBS
from datetime import datetime

DB_NAME = "/home/zhengc/DataDownloader2.7/test_sqlite_db.sqlite"
USERNAME = 'zhengc'
PASSWORD = 'czhen033'
PACKAGE_FOLDER = "/home/zhengc/DataDownloader2.7/DataPackages/"


def main():
   start_time = datetime.now()
   command_line = "getCommandLine"
   
   my_db_instance = my_sqlite_db()
   conn = my_db_instance.initial_sqlite(DB_NAME)

   web_parser_instance = parse_webpageBS()
   
   session_requests = web_parser_instance.login()   
   
   package_info = web_parser_instance.get_package_list(session_requests)   
   new_package = my_db_instance.check_new_package(conn,package_info)
   for a_pack in new_package:
      #download a package
      more_pack_info = web_parser_instance.download(a_pack[0], PACKAGE_FOLDER)
      print(more_pack_info)
      #insert to data_package
      my_db_instance.insert_values_dp_packinfo(conn, more_pack_info)
     # my_db_instance.insert_values_dp_packinfo2(conn,more_pack_info)
      
  # my_db_instance.check_dp_table(conn)
if __name__ == '__main__':
   main()

