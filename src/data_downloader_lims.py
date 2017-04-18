from my_sqlite_db import my_sqlite_db
from parse_webpageBS import parse_webpageBS
from datetime import datetime

DB_NAME = "/home/zhengc/DataDownloader2.7/test_sqlite_db.sqlite"
USERNAME = 'zhengc'
PASSWORD = 'czhen033'



def main():
   start_time = datetime.now()
   command_line = "getCommandLine"
   
   my_db_instance = my_sqlite_db()
   my_db_instance.initial_sqlite(DB_NAME)

   web_parser_instance = parse_webpageBS()
   
   session_requests = web_parser_instance.login()   
   
   package_info = web_parser_instance.get_package_list(session_requests)   
   
  # new_package = my_db_instance.check_new_package(package_info)

   print(package_info)
   # for each package_info 
if __name__ == '__main__':
   main()

