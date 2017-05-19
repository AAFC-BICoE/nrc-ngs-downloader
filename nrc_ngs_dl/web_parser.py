import requests
import os
import sys
import logging
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from datetime import datetime
from datetime import date
import time
from BeautifulSoup import BeautifulSoup


logger  = logging.getLogger('nrc_ngs_dl.web_parser')

class WebParser:
    def __init__(self, login_url, runlist_url, username, password):
        """Initialize the object by logging into the web page
        Args: 
            login_url (str): link to the login page (https://lims.bioinfo.nrc.ca/login.html)
            runlist_url (str): link to the page with a list of all the sequence runs
                               (https://lims.bioinfo.nrc.ca/lims/show_runs.html)
            username (str): username 
            password (str): password
        """
        login_data = {
            'username' : username,
            'password' : password,
            'submit' : 'Login',
            }
        session_requests = requests.Session()
        try:
            session_requests.post(login_url, verify=False, data=login_data)
        except:
            logger.info('Cannot log into the NRC-LIMS web page')
            sys.exit(1)
        self.session_requests = session_requests
        self.runlist_url = runlist_url
    
    def get_runlist(self, table_id, link_column, status_column):
        """Get a list of completed sequence runs
        Args:
            table_id (str): tags to get the table (div id runs_table)
            link_column (str): the column which contains the link to a sequence run
            status_column (str): the column to show if the sequence run is completed or not
        Returns:
            A list of links to the completed sequence runs
        """
        packages = []
        try:
            r = self.session_requests.get(self.runlist_url, verify=False)
        except:
            logger.info('Cannot access the page of run_list')
            sys.exit(1)
        soup = BeautifulSoup(r.content)
        try:
            table = self.get_table(soup, table_id)
        except:
            logger.info('Cannot get the table %s' % (table_id))
            sys.exit(1)
    
        title_row = table.findAll('tr')[0]
        keys = self.get_text_arow(title_row,'th')
        index_link = keys.index(link_column)
        index_status = keys.index(status_column)
        
        for row in table.findAll('tr')[1:]:
            cells = row.findAll('td')
            run_link_here = cells[index_link].find('a',href = True).get('href')
            #run_name_here = self.get_text_acell(cells[index_link])
            status_here = self.get_text_acell(cells[index_status])
            if status_here == 'completed':
                packages.append(run_link_here)
        
        reverse_list = list(reversed(packages))
        #print(reverse_list)
        return reverse_list   
    
    def get_runinfo(self, run_url):
        """Parse information of a sequence run
        i.e. run_name,machine_name,plate_name,platform,run_mode,
        run_type,num_cycles,quality_format,operator,creation_date,
        description,status
        Args:
            run_url(str): link to a sequence run
        Returns:
            dictionary of the information
        """
        try:
            r = self.session_requests.get(run_url, verify=False)
        except:
            logger.info('Cannot access the page of sequence run %s ' % (run_url))
            sys.exit(1)
        soup = BeautifulSoup(r.content)
        run_info = {}
        try:
            table = soup.find('table', {'class':'label_value'})
        except:
            logger.info('Cannot find the table of label_value')
            sys.exit(1)
            
        for a_row in table.findAll('tr'):
            two_cells = a_row.findAll('td')
            if len(two_cells)!=2:
                logging.info('More than two columns in table label_value')
                
            column_name = self.get_text_acell(two_cells[0])
            column_value = self.get_text_acell(two_cells[1])   
            column_name = column_name.lower()
            column_name_part = column_name.split(' ')
            link = '_'
            column_name = link.join(column_name_part)[:-1]
            run_info[column_name] = column_value
        return run_info
        
    def get_laneinfo(self, run_url, table_id, column_lane, column_link):
        """Parse information of all lanes in a sequence run,
        Args:
            run_url: link of a sequence run
            table_id: tags for parsing a table
            column_lane: the specific column which contains lane_index
            column_link: the specific column which contains a link to data
        Returns:
            A list of lanes in a sequence run 
        """
        try:
            r = self.session_requests.get(run_url, verify=False)
        except:
            logger.info('Cannot access the page of sequence run %s ' % (run_url))
            sys.exit(1)
        soup = BeautifulSoup(r.content)
        try:
            table = self.get_table(soup, table_id)
        except:
            logger.info('Cannot find the table %' % (table_id))
            sys.exit(1)
        #table = soup.find("table", {"class":"lims"})
        title_row = table.findAll('tr')[0]
        keys = self.get_text_arow(title_row,'th')
        index_lane = keys.index(column_lane)
        index_download = keys.index(column_link)
        lane_list = []
        row_index = 1
        for a_row in table.findAll('tr')[1:]:
            row_index += 1
            a_lane = []
            #a_line = self.get_text_arow(a_row,"td")
            all_cell = a_row.findAll('td')
            lane_number = self.get_text_acell(all_cell[index_lane])
            download_file_url = all_cell[index_download].find('a', href=True)  
            if lane_number != '' and len(download_file_url) == 1:
                previous_lane_end = row_index-2
                if previous_lane_end > 0:
                    lane_list[len(lane_list)-1].append(previous_lane_end)
                a_lane.append(lane_number)
                a_lane.append(download_file_url.string.strip())
                a_lane.append(download_file_url.get('href'))
                all_headers = self.session_requests.get(a_lane[2], stream=True)
                if all_headers.status_code != 200:
                    logger.info('Wrong headers %s' % (a_lane[2]))
                #print(all_headers.status_code)
                #if all_headers.status_code != 200:
                    #all_headers = self.session_requests.get(a_lane[2], stream=True)
                content_length = all_headers.headers['content-length']
                a_lane.append(content_length)
                a_lane.append((row_index))  #start of a lane
            if len(a_lane) > 3:
                lane_list.append(a_lane)
        lane_list[len(lane_list)-1].append(row_index-1)
        return lane_list
    
    def get_fileinfo(self, run_url, a_lane_info,table_id):
        """Parse information of all the fastq files within a lane 
        Args:
            run_url (str): link to a sequence run
            a_lane_info (str):
            table_id (str): tags to get the table
        Returns:
            Information of all the fastq files
        """
        file_list = []
        try:
            r = self.session_requests.get(run_url, verify=False)
        except:
            logger.info('Cannot access the page of sequence run %s ' % (run_url))
            sys.exit(1)
        soup = BeautifulSoup(r.content)
        try:
            table = self.get_table(soup, table_id)
        except:
            logger.info('Cannot find the table %s' % (table_id))
            sys.exit(1)
        title_row = table.findAll('tr')[0]
        keys = self.get_text_arow(title_row,'th')
        new_keys=[]
        for each_key in keys:
            each_key = each_key.replace('%', 'pct')
            each_key = each_key.lower()
            each_key_part = each_key.split(' ')
            link = '_'
            each_key = link.join(each_key_part)
            new_keys.append(each_key)
        file_list.append(new_keys)
        lane_start = a_lane_info[4]
        lane_end = a_lane_info[5]+1
        for a_row in table.findAll('tr')[lane_start:lane_end]:
            text_all_cell = self.get_text_arow(a_row,'td')
            file_list.append(text_all_cell)     
        return file_list
    

    def get_text_arow(self,a_row, tag):
        """Get the text for all the cells of a row
        Args:
            a_row: a row of a table
            tag (str): tag for a cell, i.e. td or th
        Returns: 
            A list of text in a row of a table
        """
        text_list = []
        all_cell = a_row.findAll(tag)
        for a_cell in all_cell:
            a_text = self.get_text_acell(a_cell)
            text_list.append(a_text)
        return text_list
    
    def get_table(self, soup, table_id):
        """Get a table with the table_id"""
        table_id_values = table_id.split()
        if table_id_values[0] =='table':
            table = soup.find(table_id_values[0], {table_id_values[1]:table_id_values[2]})
        else:
            a_tag = soup.find(table_id_values[0], {table_id_values[1]:table_id_values[2]})
            table = a_tag.findAll('table')[0]
        return table

    def get_text_acell(self,a_cell):
        """ Get the text in a specific cell of a table"""
        a_text = a_cell.findAll(text = True)
        a_text = [i for i in a_text if i not in ('\n', '')]
        if len(a_text) == 0:
            a_text = ''
        else:
            a_text = a_text[0].strip()
        return a_text
    
    def download_zipfile(self, urlAddress, outputFileName):
        """Download a zip file
        Args:
            urlAddress: link to the file
            outputFileName: path and file name to hold the file
        Returns:
            Date to download the file
            Time (in minutes) spend on downloading the file
            Size of the file 
        """
        time_and_size = []
        download_date = date.today().strftime('%m/%d/%Y')
        time_and_size.append(download_date)
        start = time.time()
        chunkSize = 4096 * 512 * 4
        totalSize = 0
        res = self.session_requests.get(urlAddress, stream=True)
        with open(outputFileName, 'wb') as output:
            chunknumber = 0
            for chunk in res.iter_content(chunk_size=chunkSize, decode_unicode=False):
                if chunk:
                    totalSize = totalSize + chunkSize
                    chunknumber += 1
                    output.write(chunk)
                    print(datetime.now(), totalSize)
        end = time.time()
        time_in_min = (end - start) / 60
        time_and_size.append('%.1f' % time_in_min)
        fileSize = os.stat(outputFileName).st_size
        time_and_size.append(str(fileSize))
        return time_and_size
        
        



