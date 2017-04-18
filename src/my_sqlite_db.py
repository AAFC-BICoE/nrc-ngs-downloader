import os
from datetime import datetime
import sqlite3

class my_sqlite_db:
   def initial_sqlite(self,db_name):
      print(db_name) 
      if os.path.isfile(db_name) == False:
         conn = sqlite3.connect(db_name)
         c = conn.cursor()
         c.execute("CREATE TABLE application_action (action_ID INT PRIMARY KEY, start_time TEXT, end_time TEXT, access_success TEXT, command_line TEXT)")
         c.execute("CREATE TABLE data_packages (package_ID INT PRIMARY KEY, action_ID INT, download_date TEXT, time_for_downding_inMins INT, package_size REAL, url_address TEXT, SHA256_code TEXT, run_name TEXT, date_creation TEXT,plate_name TEXT, platform TEXT, operator TEXT, description TEXT, status TEXT )")
         c.execute("CREATE TABLE data_files (file_ID INT, package_ID INT, new_name TEXT, original_name TEXT, file_size REAL, sample_name TEXT, biomaterial TEXT, biomaterial_type TEXT, comments TEXT, principal_investigator TEXT, MID_tag TEXT, barcode TEXT, num_reads INT pct_reads_in_lane REAL, folder_name TEXT )")
                                    
         conn.commit()
      else:
         conn = sqlite3.connect(db_name)
      return conn

   def insert_value_aa_st(self, cur, args):
      cur.execute('INSERT INTO application_action (action_ID, start_time, end_time,access_success, command_line) VALUES (?,?,?,?,?)', (args[0], args[1],args[2],args[3],args[4]))

      
   def insert_values_dp_packinfo(self, a_pack_info):
      if len(a_pack_info)== 8:
         cur.execute('INSERT INTO data_packages(url_address,run_name,plate_name,platform, operator,date_creation,description,status) VALUES (?,?,?,?,?,?,?,?)',a_pack_info)
   
   def check_new_package(self, all_pack_info):
      for a_package in all_pack_info:
         print(a_package)
               
