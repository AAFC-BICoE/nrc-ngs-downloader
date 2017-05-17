import os
import sys
from datetime import datetime
import sqlite3
import logging

logger  = logging.getLogger('nrc_ngs_dl.lims_database')

class LimsDatabase:
    
    ####################################
    #method to connect and disconnect the database
     
    #initial the database if not exist
    #otherwise simply connect to the database
    def __init__(self,db_name):
        self.db_name = db_name
        if os.path.isfile(db_name) == False:
            try:
                conn = sqlite3.connect(db_name)
            except:
                logger.info('Cannot access the database %s' %(db_name))
                sys.exit(1)
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
            try:
                conn = sqlite3.connect(db_name)
            except:
                logger.info('Cannot access the database %s' % (db_name))
                sys.exit(1)
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
        """Add lane info to SQLite database
        :param rowid:describe what this is
        :param run_url: 
        :return: dfsdfsd 
        """
        cur = self.conn.cursor()
        table_name = 'data_packages'
        column_names = ('pack_info_url','lane_index', 'package_name', 'pack_data_url', 'http_header')
        column_values = (run_url,str(a_lane_info[0]),a_lane_info[1],a_lane_info[2],a_lane_info[3])
        id_name = 'package_ID'
        for index in range(len(column_names)):
            self.insert_a_value(table_name, column_names[index], column_values[index], id_name, rowid)
        self.conn.commit()
        
    #insert package_size, date_to_download and total time to download(in minutes)   
    def insert_package_info(self,rowid, date_time_size):
        '''
        '''
        cur = self.conn.cursor()
        table_name = 'data_packages'
        column_names = ('download_date','time_for_downloading', 'package_size')
        id_name = 'package_ID'
        for index in range(len(column_names)):
            self.insert_a_value(table_name, column_names[index], date_time_size[index], id_name, rowid)
        self.conn.commit()
        
          
    def insert_file_info(self, package_id, all_file_info):
        cur = self.conn.cursor()
        rowid = self.get_last_row_id('data_files','file_ID')+1
        for a_row in all_file_info[1:]:
            if len(a_row) != len(all_file_info[0]):
                logger.info('different length between keys and values')
            else:
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
    #method to check new runs and re-processed runs
    #by considering run_name, lane_index and http-header(content_length)
    def check_new_run(self,a_run_info, a_lane_info):
        """
        """
        cur = self.conn.cursor()
        run_name = a_run_info['run_name']
        lane_index = a_lane_info[0]
        content_length = a_lane_info[3]
        cur.execute('SELECT http_header FROM data_packages WHERE run_name =? and lane_index = ?', (run_name, lane_index,))
        all_rows = cur.fetchall()
        if len(all_rows) == 1:
            content_length_old = all_rows[0][0]
            #print(content_length_old, content_length)
            if content_length_old == content_length:
                return 1  #old data, do nothing
            else:
                return 3  # reprocessed data
            
        if len(all_rows) == 0:
            return 2  # new data, download data and insert info into database
        
        return 1    # old data 
    
    
    ################################################
    #methods to print out tables in SQLite database    
     
    def check_dp_table(self):
        """print out all rows in data_package table"""
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM data_packages')
        all_rows = cur.fetchall()
        for a_row in all_rows:
            print(a_row)
    
    
    def check_df_table(self):
        """print out all rows in data_file table"""
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM data_files')
        all_rows = cur.fetchall()
        for a_row in all_rows[-10:-1]:
            print(a_row)
    

    def get_fieldname(self,table_name):
        """print out column names of a table"""
        cur = self.conn.cursor()
        command_string = 'select * from '+table_name
        cur.execute(command_string)
        fieldnames = [f[0] for f in cur.description]
        print(fieldnames)
        return fieldnames
    
    def delete_old_run(self,a_run_info, a_lane_info):
        """delete old information related to re-processed sequence run"""
        cur = self.conn.cursor()
        run_name = a_run_info['run_name']
        lane_index = a_lane_info[0]
        cur.execute('SELECT package_ID FROM data_packages WHERE run_name =? and lane_index = ?', (run_name, lane_index,))
        all_rows = cur.fetchall()
        if len(all_rows) == 1:
            package_ID_old = all_rows[0][0]
            cur.execute('DELETE FROM data_packages WHERE package_ID =?',(package_ID_old,))
            cur.execute('DELETE FROM data_files WHERE package_ID =?',(package_ID_old,))
        if len(all_rows) == 0:
            logger.info('Cannot find information of re-processed data')
        if len(all_rows) > 1:
            logger.info('duplicate information of re-processed data')
            
    #######################################################
    #some methods to modify the database, 
    #only useful for testing the method: check_new_run
    
    
    def delete_last_run(self):
        """delete last row in table data_package"""
        cur = self.conn.cursor()
        rowid = self.get_last_row_id('data_packages','package_ID')
        print(rowid)
        cur.execute('DELETE FROM data_packages WHERE package_ID = ?', (rowid,))
        self.conn.commit()
    
    
    def delete_a_run(self, rowid):
        """delete a sequence run with the row_id, if it exists"""
        cur = self.conn.cursor()
        cur.execute('DELETE FROM data_packages WHERE package_ID = ?', (rowid,))
        self.conn.commit()
    
    def modify_http_header(self, package_ID, new_value):
        """change the header(content_length), for testing re-processed runs"""
        cur = self.conn.cursor()
        command_string = 'UPDATE data_packages SET http_header = \''+new_value+'\' WHERE package_ID = ?'
        cur.execute(command_string, (package_ID,)) 
        self.conn.commit()
        
        
