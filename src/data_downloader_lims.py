from my_sqlite_db import my_sqlite_db
from parse_webpageBS import parse_webpageBS
from datetime import datetime

DB_NAME = "/home/zhengc/NRC-LIMS-dataDownloader/test_sqlite_db.sqlite"
USERNAME = 'zhengc'
PASSWORD = 'czhen033'
PACKAGE_FOLDER = "/home/zhengc/NRC-LIMS-dataDownloader/DataPackages/"
PATH_DEST = "/home/zhengc/NRC-LIMS-dataDownloader/DataFiles/"

def main():
   start_time = datetime.now()
   command_line = "getCommandLine"
   
   my_db_instance = my_sqlite_db()
   conn = my_db_instance.initial_sqlite(DB_NAME)

   web_parser_instance = parse_webpageBS()
   
   session_requests = web_parser_instance.login()   
   smallest_package = '161206_M01549_0132_000000000-AWWU4'
   package_info = web_parser_instance.get_package_list(session_requests)   
   new_package = my_db_instance.check_new_package(conn,package_info)
   for a_pack in new_package:
     # print(a_pack[1])
      #print(smallest_package)
      if a_pack[1] == smallest_package:
         print("smallest")
         a_pack_info,files_info = web_parser_instance.action_for_a_package(a_pack[0], PACKAGE_FOLDER,PATH_DEST)
        # print(a_pack_info)
         #print(files_info)
         #my_db_instance.insert_values_packinfo(conn, a_pack_info)
         #my_db_instance.insert_values_fileinfo(conn, files_info)
      #my_db_instance.insert_values_dp_packinfo2(conn,more_pack_info)
      
      #my_db_instance.check_dp_table(conn)
      #my_db_instance.check_df_table(conn)
   conn.close()
if __name__ == '__main__':
   main()

