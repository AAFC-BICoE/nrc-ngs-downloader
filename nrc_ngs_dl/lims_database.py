import logging
import os
import sqlite3
import sys


#from datetime import datetime
logger  = logging.getLogger('nrc_ngs_dl.lims_database')

class LimsDatabase:
    RUN_OLD=1
    RUN_NEW=2
    RUN_REPROCESSED=3
    def __init__(self,db_name):
        """Initialize the database if not exist; 
        otherwise simply connect to the database
        """
        self.db_name = db_name
        logger.info('Connect to database...')
        if os.path.isfile(db_name) == False:
            try:
                conn = sqlite3.connect(db_name)
            except:
                logger.info('Cannot access the database %s' %(db_name))
                raise 
            c = conn.cursor()
            c.execute('''CREATE TABLE data_packages (
                            package_id INTEGER PRIMARY KEY AUTOINCREMENT,action_id INT,
                            download_date TEXT,time_for_downloading REAL,
                            package_size REAL,package_name TEXT,
                            pack_info_url TEXT,pack_data_url TEXT,
                            lane_index INT,run_name TEXT,
                            machine_name TEXT,plate_name TEXT,
                            platform TEXT,run_mode TEXT,
                            run_type TEXT,num_cycles INT,
                            quality_format TEXT,operator TEXT,
                            creation_date TEXT,description TEXT,
                            status TEXT,http_content_length INT,
                            FOREIGN KEY(action_id) REFERENCES application_action(action_id)
                            )''')
            
            c.execute('''CREATE TABLE data_files (
                            file_id INTEGER PRIMARY KEY AUTOINCREMENT, package_id INT,
                            sample_name TEXT, biomaterial TEXT, 
                            biomaterial_type TEXT, 
                            comments TEXT, principal_investigator TEXT, 
                            mid_tag TEXT, barcode TEXT, 
                            numreads INT, pct_of_reads_in_lane REAL, 
                            new_name TEXT, original_name TEXT,
                            file_size INT,folder_name TEXT, SHA256 TEXT,
                            FOREIGN KEY(package_id) REFERENCES data_packages(package_id)
                            )''')
            c.execute('''CREATE TABLE application_action (
                            action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            start_time TEXT, end_time TEXT,
                            machine_ip TEXT, directory_name TEXT,
                            package_downloaded INT,
                            command_line TEXT,
                            version INT 
                        )''')
            conn.commit()
           
        else:
            try:
                conn = sqlite3.connect(db_name)
            except:
                logger.info('Cannot access the database %s' % (db_name))
                raise
            
        self.conn = conn
    
    #close the database
    def disconnect(self):
        self.conn.close()
    
    
    ###############################################
    #methods to insert values into different tables
     
     
    def insert_action_info(self,action_info):
        cur = self.conn.cursor()
        all_pair = action_info.items()
        table_column = self.get_fieldname('application_action')
        column_name, column_value = self.validate_pair(all_pair, table_column)
        command_str = 'INSERT into application_action '+ column_name
        cur.execute(command_str, column_value)
        rowid = self.get_last_row_id('application_action','action_id')
        self.conn.commit()
        return rowid

    
    def insert_end_time(self,action_id,end_time): 
        cur = self.conn.cursor()
        command_str = 'UPDATE application_action SET end_time ="'\
                       + end_time + '" WHERE action_id = ?'              
        cur.execute(command_str,(action_id,))
        self.conn.commit() 
        
    def update_package_downloaded(self, package_downloaded, action_id):
        cur = self.conn.cursor()
        command_str = 'UPDATE application_action SET package_downloaded = ?  WHERE action_id = ?'              
        
        cur.execute(command_str,(package_downloaded, action_id,))
        self.conn.commit() 
        
    def insert_run_info(self, run_info, action_id):
        """Add information of a sequence run to SQLite database
        i.e. run_name,machine_name,plate_name,platform,run_mode,
        run_type,num_cycles,quality_format,operator,creation_date,
        description,status
        Args:
            run_info (dictionary): information of a sequence run
        """
        cur = self.conn.cursor()
       
        table_column = self.get_fieldname('data_packages')
        run_info['action_id'] = action_id
        all_pair = run_info.items()
        column_name, column_value = self.validate_pair(all_pair, table_column)
        
        command_str = 'INSERT into data_packages '+ column_name
        #cur.execute('INSERT INTO data_packages (package_ID) VALUES (?)',(rowid,))
        cur.execute(command_str, column_value)
        rowid = self.get_last_row_id('data_packages','package_id')
        self.conn.commit()
        return rowid
     
      
    def validate_pair(self, all_pair, table_column):
        column_name = '('
        question = ' VALUES ('
        column_value = []
        for a_pair in all_pair:
            key = a_pair[0]
            value = a_pair[1]
            if key in table_column:
                column_name = column_name+key+','
                question = question+'?,'
                column_value.append(value)
            else:
                logger.warn('Cannot find %s in database'% key )
        column_name = column_name[:-1]+')' 
        question = question[:-1]+')'
        column_name = column_name + question
        return column_name, column_value 


    def insert_lane_info(self, rowid, run_url, a_lane_info):
        """Add information of a lane to SQLite database
        i.e.lane_index, file name of the zipped file, link to the zipped file, link to the sequence run
        http_header, 
        Args:
            rowid (int): primary key of the record for this lane
            run_url (str): link to the sequence run
            a_lane_info (list): information of a lane 
        """
        cur = self.conn.cursor()
        command_str = 'UPDATE data_packages SET pack_info_url ="'\
                       + run_url+'",lane_index = '\
                       + a_lane_info['lane_index']+ ',package_name = "'\
                       + a_lane_info['package_name'] +'",pack_data_url = "'\
                       + a_lane_info['pack_data_url'] +'",http_content_length ='\
                       + a_lane_info['http_content_length'] + ' WHERE package_id = ?'              
        cur.execute(command_str,(rowid,))
        self.conn.commit()
        
          
    def insert_package_info(self,rowid, date_time_size):
        """Add information of a zipped file to SQLite database
        i.e. date, time (in minutes) and size of the file
        Args:
            rowid (int): primary key of the record for this zipped file
        """
        cur = self.conn.cursor()
        command_str = 'UPDATE data_packages SET download_date ="'\
                       + date_time_size[0]+'",time_for_downloading = '\
                       + date_time_size[1]+ ',package_size = '\
                       + date_time_size[2]+ ' WHERE package_id = ?'
                                   
        cur.execute(command_str,(rowid,))
        self.conn.commit()
        
          
    def insert_file_info(self, package_id, all_file_info, lane_index):
        """Add information of all the fastq files to SQLite database
        i.e.
        Args:
            package_id (int): primary key in table data_package, foreign key in table data_file
            all_file_info (list): 
        """
        cur = self.conn.cursor()
        table_column = self.get_fieldname('data_files')
        for a_row in all_file_info:
            if a_row['lane_index'] == lane_index:
                a_row['package_id'] = package_id
                all_pair = a_row.items()
                column_name, column_value = self.validate_pair(all_pair, table_column)
                command_str = 'INSERT into data_files '+ column_name
                cur.execute(command_str, column_value)
        self.conn.commit()
   
   
    def get_last_row_id(self,table_name, id):
        cur = self.conn.cursor()
        command_string = 'SELECT max('+id+') FROM '+table_name
        cur.execute(command_string)
        max_id = cur.fetchone()[0]
        if max_id is None:
            max_id = 0
        return max_id
        
        
    def get_fieldname(self,table_name):
        """Get the column names of a table"""
        cur = self.conn.cursor()
        command_string = 'select * from '+table_name
        cur.execute(command_string)
        fieldnames = [f[0] for f in cur.description]
        return fieldnames
   
   
    def get_run_case(self,a_run_info, a_lane_info):
        """check a sequence run against database 
        by considering run_name, lane_index and http-header(content_length)
        """
        cur = self.conn.cursor()
        run_name = a_run_info['run_name']
        lane_index = a_lane_info['lane_index']
        content_length = a_lane_info['http_content_length']
        cur.execute('SELECT http_content_length FROM data_packages WHERE run_name =? and lane_index = ?', (run_name, lane_index,))
        all_rows = cur.fetchall()
        if len(all_rows) == 1:
            content_length_old = all_rows[0][0]
            if content_length_old == content_length:
                return self.RUN_OLD  #old data, do nothing
            else:
                return self.RUN_REPROCESSED  # reprocessed data
        if len(all_rows) == 0:
            return self.RUN_NEW  # new data, download data and insert info into database
        return self.RUN_OLD    # old data 
    
    
    def delete_old_run(self,a_run_info, a_lane_info):
        """delete old information related to re-processed sequence run"""
        cur = self.conn.cursor()
        run_name = a_run_info['run_name']
        lane_index = a_lane_info['lane_index']
        cur.execute('SELECT package_id FROM data_packages WHERE run_name =? and lane_index = ?', (run_name, lane_index,))
        all_rows = cur.fetchall()
        if len(all_rows) == 1:
            package_ID_old = all_rows[0][0]
            cur.execute('DELETE FROM data_packages WHERE package_id =?',(package_ID_old,))
            cur.execute('DELETE FROM data_files WHERE package_id =?',(package_ID_old,))
        if len(all_rows) == 0:
            logger.error('Cannot find information of re-processed data')
        if len(all_rows) > 1:
            logger.error('duplicate information of re-processed data')
     
     
    ##############all the methods below can be removed###############
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
                   
    #some methods to modify the database, 
    #only useful for testing the method: check_new_run
    def delete_last_run(self):
        """delete last row in table data_package"""
        cur = self.conn.cursor()
        rowid = self.get_last_row_id('data_packages','package_id')
        print(rowid)
        cur.execute('DELETE FROM data_packages WHERE package_id = ?', (rowid,))
        cur.execute('DELETE FROM data_files WHERE package_id =?',(rowid,))
        self.conn.commit()
    
    def delete_a_run(self, rowid):
        """delete a sequence run with the row_id, if it exists"""
        cur = self.conn.cursor()
        cur.execute('DELETE FROM data_packages WHERE package_id = ?', (rowid,))
        cur.execute('DELETE FROM data_files WHERE package_id =?',(rowid,))
        self.conn.commit()
    
    def modify_http_header(self, package_ID, new_value):
        """change the header(content_length), for testing re-processed runs"""
        cur = self.conn.cursor()
        command_string = 'UPDATE data_packages SET http_header = \''+new_value+'\' WHERE package_ID = ?'
        cur.execute(command_string, (package_ID,)) 
        self.conn.commit()
        
    def insert_a_value(self,table_name, column_name, column_value,id_name, rowid):
        cur = self.conn.cursor()
        if self.has_column(table_name, column_name):
            command_string = 'UPDATE '+table_name+' SET ' + column_name + ' = \''+ column_value +'\' WHERE '+id_name +'= ?'
            cur.execute(command_string, (rowid,))   
