import os
from datetime import datetime
import sqlite3

class my_sqlite_db:
   def initial_sqlite(self,db_name):
     # print(db_name) 
      if os.path.isfile(db_name) == False:
         conn = sqlite3.connect(db_name)
         c = conn.cursor()
        # c.execute("CREATE TABLE application_action (action_ID INT PRIMARY KEY, start_time TEXT, end_time TEXT, access_success TEXT, command_line TEXT)")
         c.execute("CREATE TABLE data_packages (package_ID INT PRIMARY KEY, action_ID INT, download_date TEXT, time_for_downloading TEXT, package_size REAL, package_name TEXT, pack_info_url TEXT, pack_data_url TEXT, run_name TEXT, machine_name TEXT, plate_name TEXT, platform TEXT,run_mode TEXT, run_type TEXT, num_cycles INT, quality_format TEXT, operator TEXT, date_creation TEXT, description TEXT, status TEXT, http_header TEXT )")
         c.execute("CREATE TABLE data_files (file_ID INT, package_ID INT, new_name TEXT, original_name TEXT, file_size REAL, sample_name TEXT, biomaterial TEXT, biomaterial_type TEXT, comments TEXT, principal_investigator TEXT, MID_tag TEXT, barcode TEXT, num_reads TEXT, pct_reads_in_lane TEXT, folder_name TEXT, SHA256 TEXT)")
                                 
         conn.commit()
      else:
         conn = sqlite3.connect(db_name)
      return conn

   def insert_value_aa_st(self, conn, args):
      cur = conn.cursor()
      cur.execute('INSERT INTO application_action (action_ID, start_time, end_time,access_success, command_line) VALUES (?,?,?,?,?)', (args[0], args[1],args[2],args[3],args[4]))
      conn.commit() 
      
   def insert_values_packinfo(self,conn, a_pack_info):
      if len(a_pack_info)== 17:
         cur = conn.cursor()
         cur.execute('INSERT INTO data_packages(pack_info_url,download_date,run_name,machine_name,plate_name,platform,run_type, num_cycles,quality_format, operator, status, date_creation,description, package_name, pack_data_url, time_for_downloading, package_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',a_pack_info)
         conn.commit()
      if len(a_pack_info)== 18:
         cur = conn.cursor()
         cur.execute('INSERT INTO data_packages(pack_info_url,download_date,run_name,machine_name,plate_name,platform,run_mode,run_type, num_cycles,quality_format, operator, status, date_creation,description, package_name, pack_data_url, time_for_downloading, package_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',a_pack_info)
         conn.commit()

  
   def insert_values_fileinfo(self, conn, all_file_info):
      for a_row in all_file_info:
         print("info for a file", a_row)
         if len(a_row) == 13:
            cur = conn.cursor()
            cur.execute('INSERT INTO data_files(sample_name,biomaterial,biomaterial_type, comments, principal_investigator,MID_tag, TEXT,barcode TEXT, num_reads, pct_reads_in_lane,original_name, new_name,SHA256,file_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', a_row)
         if len(a_row) == 11:
            cur = conn.cursor()
            cur.execute('INSERT INTO data_files(sample_name,biomaterial,biomaterial_type, comments, principal_investigator, num_reads, pct_reads_in_lane,original_name, new_name,SHA256,file_size) VALUES (?,?,?,?,?,?,?,?,?,?,?)',a_row)
      conn.commit()
  

   def insert_values_dp_packinfo2(self,conn, a_pack_info):
  #    if len(a_pack_info)==8):
      print(a_pack_info)
   
   def check_new_package(self, conn,all_pack_info):
      cur = conn.cursor()
      my_list = []
      for a_package in all_pack_info:
         if len(a_package)==8:
            #cur.execute('SELECT run_name FROM data_packages WHERE (run_name, date_creation) =(?,?)', (a_package[1],a_package[5]))
            cur.execute('SELECT * FROM data_packages WHERE run_name =?', (a_package[1],))
            all_rows = cur.fetchall()
            if len(all_rows) == 0:
               my_list.append(a_package)       
      return my_list   

   def check_dp_table(self, conn):
      cur = conn.cursor()
      cur.execute('SELECT * FROM data_packages')
      all_rows = cur.fetchall()
      index = 0
      for a_row in all_rows:
         print(index,a_row)
         index += 1
 
   def check_df_table(self, conn):
      cur = conn.cursor()
      cur.execute('SELECT * FROM data_files')
      all_rows = cur.fetchall()
      index = 0
      for a_row in all_rows:
         print(index,a_row)
         index += 1

