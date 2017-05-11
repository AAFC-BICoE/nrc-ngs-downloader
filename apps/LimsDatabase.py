import os
from datetime import datetime
import sqlite3

class LimsDatabase:
    
    ####################################
    #method to connect and disconnect the database
     
    #initial the database if not exist
    #otherwise simply connect to the database
    def __init__(self,db_name):
        self.db_name = db_name
        if os.path.isfile(db_name) == False:
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            c.execute("CREATE TABLE data_packages (package_ID INT PRIMARY KEY, action_ID INT)")
            c.execute('ALTER TABLE data_packages ADD COLUMN download_date TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN time_for_downloading TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN package_size TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN package_name TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN pack_info_url TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN pack_data_url TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN lane_index TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN run_name TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN machine_name TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN plate_name TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN platform TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN run_mode TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN run_type TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN num_cycles INT')
            c.execute('ALTER TABLE data_packages ADD COLUMN quality_format TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN operator TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN  creation_date TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN description TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN status TEXT')
            c.execute('ALTER TABLE data_packages ADD COLUMN http_header TEXT')
            
            c.execute("CREATE TABLE data_files (file_ID INT PRIMARY KEY, package_ID INT)")
            other_column = [["sample_name","TEXT"], ["biomaterial","TEXT"], ["biomaterial_type","TEXT"], 
                            ["comments","TEXT"], ["principal_investigator","TEXT"], ["mid_tag","TEXT"], 
                            ["barcode","TEXT"], ["numreads","TEXT"], ["pct_of_reads_in_lane","TEXT"], 
                            ["new_name","TEXT"], ["original_name","TEXT"],
                            ["file_size","REAL"],["folder_name","TEXT"], ["SHA256","TEXT"],
                            ]
            for a_column in other_column:
                column_name = a_column[0]
                column_type = a_column[1]
                add_string = 'ALTER TABLE data_files ADD COLUMN '+column_name+ " "+column_type;
                c.execute(add_string)
    
            conn.commit()
           
        else:
            conn = sqlite3.connect(db_name)
        self.conn = conn
    
    #close the database
    def disconnect(self):
        self.conn.close()
    
    
    ###############################################
    #methods to insert values into different tables
    
    #insert sequence run information, which scrapped from NRC-LIMS, into data_packages
    #run_name,machine_name,plate_name,platform,run_mode,run_type,num_cycles,
    #quality_format,operator,creation_date,description,status
    def insert_run_info(self, run_info):
        cur = self.conn.cursor()
        rowid = self.get_last_row_id('data_packages','package_ID')+1
        all_pair = run_info.items()
        cur.execute('INSERT INTO data_packages (package_ID) VALUES (?)',(rowid,))
        for a_pair in all_pair: 
            column_name = a_pair[0]
            column_value = a_pair[1]
            table_name = 'data_packages'
            id_name = 'package_ID'
            self.insert_a_value(table_name,column_name,column_value,id_name, rowid)
        self.conn.commit()
        return rowid  
    
    #insert lane information into data_packages
    #lane_index, information about the zipped file for each lane(package_name/file_name, pack_data_url/fileLink, http-header)
    # and pack_info_url(run_url)
    def insert_lane_info(self, rowid, run_url, a_lane_info):
        cur = self.conn.cursor()
        command_string = 'UPDATE data_packages SET pack_info_url = \''+run_url+'\' WHERE package_ID = ?'
        cur.execute(command_string, (rowid,))
        command_string = 'UPDATE data_packages SET lane_index = \''+str(a_lane_info[0])+'\' WHERE package_ID = ?'
        cur.execute(command_string, (rowid,))
        command_string = 'UPDATE data_packages SET package_name = \''+a_lane_info[1]+'\' WHERE package_ID = ?'
        cur.execute(command_string, (rowid,))
        command_string = 'UPDATE data_packages SET pack_data_url = \''+a_lane_info[2]+'\' WHERE package_ID = ?'
        cur.execute(command_string, (rowid,))
        if len(a_lane_info) == 6:
            command_string = 'UPDATE data_packages SET http_header = \''+str(a_lane_info[3])+'\' WHERE package_ID = ?'
            cur.execute(command_string, (rowid,))
        self.conn.commit()
    
    #insert package_size, date_to_download and total time to download(in minutes)   
    def insert_package_info(self,rowid, date_time_size):
        cur = self.conn.cursor()
        command_string = 'UPDATE data_packages SET download_date = \''+date_time_size[0]+'\' WHERE package_ID = ?'
        cur.execute(command_string, (rowid,))
        command_string = 'UPDATE data_packages SET time_for_downloading = \''+date_time_size[1]+'\' WHERE package_ID = ?'
        cur.execute(command_string, (rowid,))
        command_string = 'UPDATE data_packages SET package_size = \''+date_time_size[2]+'\' WHERE package_ID = ?'
        cur.execute(command_string, (rowid,))
        self.conn.commit()
        
    
    #   
    def insert_file_info(self, package_id, all_file_info):
        cur = self.conn.cursor()
        rowid = self.get_last_row_id('data_files','file_ID')+1
        for a_row in all_file_info[1:]:
            cur.execute('INSERT INTO data_files (file_ID,package_ID) VALUES (?,?)',(rowid,package_id,))
            for i in range(len(a_row)):
                column_name = all_file_info[0][i]
                column_value = a_row[i]
                table_name = 'data_files'
                id_name = 'file_ID'
                self.insert_a_value(table_name,column_name,column_value,id_name, rowid)
            rowid += 1
        self.conn.commit()
    
    
    def get_last_row_id(self,table_name, id):
        cur = self.conn.cursor()
        command_string = 'SELECT max('+id+') FROM '+table_name
        cur.execute(command_string)
        max_id = cur.fetchone()[0]
        if max_id is None:
            max_id = 0
        print(max_id)
        return max_id
        
    def insert_a_value(self,table_name, column_name, column_value,id_name, rowid):
        cur = self.conn.cursor()
        if self.has_column(table_name, column_name):
            command_string = 'UPDATE '+table_name+' SET ' + column_name + ' = \''+ column_value +'\' WHERE '+id_name +'= ?'
            cur.execute(command_string, (rowid,))
        
    def has_column(self, table_name, column_name): 
        cur = self.conn.cursor()
        command_string = 'select * from '+table_name
        cur.execute(command_string)
        fieldnames = [f[0] for f in cur.description]
        if column_name in fieldnames:
            return True
        return False
    
    ############################################
    #methods to check new sequence runs and reprocessed runs.    
    
    #method to check new sequence runs,(remove the method?)
    #the conditions for this method are:
    #1: one lane in each run  2:no re-processed runs 
    def check_new_run_list(self, all_run_list):
        cur = self.conn.cursor()
        my_list = []
        for a_package in all_run_list:
            if len(a_package)==8:
                cur.execute('SELECT * FROM data_packages WHERE run_name =?', (a_package[1],))
                all_rows = cur.fetchall()
                if len(all_rows) == 0:
                    my_list.append(a_package)       
        return my_list 
    
    #method to check new runs and re-processed runs
    #by considering run_name, lane_index and http-header(content_length)
    def check_new_run(self,a_run_info, a_lane_info):
        cur = self.conn.cursor()
        run_name = a_run_info['run_name']
        lane_index = a_lane_info[0]
        content_length = a_lane_info[3]
        cur.execute('SELECT http_header FROM data_packages WHERE run_name =? and lane_index = ?', (run_name, lane_index,))
        all_rows = cur.fetchall()
        if len(all_rows) == 1 and all_rows[0] == content_length:
            return 1   # old data, do nothing
        if len(all_rows) == 0:
            return 2  # new data, download data and insert info into database
        
        return 3    # re-processed data 
    
    
    ################################################
    #methods to print out tables in SQLite database    
    
    #print out all rows in data_packages table   
    def check_dp_table(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM data_packages')
        all_rows = cur.fetchall()
        for a_row in all_rows:
            print(a_row)
    
    #print out all rows in data_file table
    def check_df_table(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM data_files')
        all_rows = cur.fetchall()
        for a_row in all_rows[-10:-1]:
            print(a_row)
    
    #print out column names in tables
    def get_fieldname(self,table_name):
        cur = self.conn.cursor()
        command_string = 'sselect * from '+table_name
        cur.execute(command_string)
        fieldnames = [f[0] for f in cur.description]
        print(fieldnames)
        return fieldnames
    
    
    #######################################################
    #some methods to modify the database, 
    #only useful for testing the method: check_new_run
    
    #delete last row in table data_package
    def delete_last_run(self):
        cur = self.conn.cursor()
        rowid = self.get_last_row_id('data_packages','package_ID')
        print(rowid)
        cur.execute('DELETE FROM data_packages WHERE package_ID = ?', (rowid,))
        self.conn.commit()
    
    #delete a row with the row_id, if it exists 
    def delete_a_run(self, rowid):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM data_packages WHERE package_ID = ?', (rowid,))
        self.conn.commit()
    
    #change the header(content_length), for testing re-processed runs 
    def modify_http_header(self, package_ID, new_value):
        cur = self.conn.cursor()
        command_string = 'UPDATE data_packages SET http_header = \''+new_value+'\' WHERE package_ID = ?'
        cur.execute(command_string, (package_ID,)) 
        self.conn.commit()
        
        