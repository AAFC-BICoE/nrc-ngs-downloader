from bs4 import BeautifulSoup
from datetime import date
import logging
import math
import os
import requests
import time
# import requests.packages.urllib3
# requests.packages.urllib3.disable_warnings()

logger = logging.getLogger('nrc_ngs_dl.web_parser')


def get_table(soup, table_id):
    """Get a table with the table_id"""
    table_id_values = table_id.split()
    if table_id_values[0] == 'table':
        table = soup.find(table_id_values[0], {table_id_values[1]: table_id_values[2]})
    else:
        a_tag = soup.find(table_id_values[0], {table_id_values[1]: table_id_values[2]})
        table = a_tag.findAll('table')[0]
    return table


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
            'username': username,
            'password': password,
            'submit': 'Login',
            }
        session_requests = requests.Session()
        try:
            session_requests.post(login_url, data=login_data)
        except:
            logger.error(f'Wrong address of login page {login_url}')
            raise
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
        
        r = self.session_requests.get(self.runlist_url)
        if r.url != self.runlist_url:
            logger.error('Failed to login, check your username, password and link to run_list page {self.runlist_url}')
            raise
        soup = BeautifulSoup(r.content, features="html.parser")
        try:
            table = get_table(soup, table_id)
        except:
            logger.error('Cannot get the table {table_id}')
            raise
    
        title_row = table.findAll('tr')[0]
        keys = self.get_text_a_row(title_row, 'th')
        index_link = keys.index(link_column)
        index_status = keys.index(status_column)
        
        for row in table.findAll('tr')[1:]:
            cells = row.findAll('td')
            run_link_here = cells[index_link].find('a', href=True).get('href')
            status_here = self.get_text_a_cell(cells[index_status])
            if status_here == 'completed':
                packages.append(run_link_here)
       
        reverse_list = list(reversed(packages))
        logger.debug('The list of all runs: {reverse_list}')
        return reverse_list   
    
    def get_run_info(self, run_url):
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
            r = self.session_requests.get(run_url)
        except:
            logger.warning(f'Cannot access the page of sequence run {run_url}')
            raise
        soup = BeautifulSoup(r.content, features="html.parser")
        run_info = {}
        try:
            table = soup.find('table', {'class': 'label_value'})
        except:
            logger.warning('Cannot find the run info table')
            raise
            
        for a_row in table.findAll('tr'):
            two_cells = a_row.findAll('td')
            if len(two_cells) != 2:
                logging.warning('More than two columns in run info table')
                raise
            column_name = self.get_text_a_cell(two_cells[0])
            column_value = self.get_text_a_cell(two_cells[1])
            column_name = column_name.lower()
            column_name_part = column_name.split(' ')
            link = '_'
            column_name = link.join(column_name_part)[:-1]
            run_info[column_name] = column_value
        logger.debug("run_url %s and run_info %s" % (run_url, run_info))
        return run_info
        
    def get_lane_info(self, run_url, table_id, column_lane, column_link):
        """Parse information of all lanes in a sequence run,
        Args:
            run_url: link of a sequence run
            table_id: tags for parsing a table
            column_lane: the specific column which contains lane_index
            column_link: the specific column which contains a link to data
        Returns:
            A list of lanes in a sequence run 
        """
        lane_list = []
        file_list = []
        try:
            r = self.session_requests.get(run_url)
        except:
            logger.warning(f'Cannot access the page of sequence run {run_url}')
            raise
        soup = BeautifulSoup(r.content, features="html.parser")
        try:
            table = get_table(soup, table_id)
        except:
            logger.warning(f'Cannot find the table {table_id}')
            raise
        title_row = table.findAll('tr')[0]
        keys = self.get_text_a_row(title_row, 'th')
        index_lane = keys.index(column_lane)
        index_download = keys.index(column_link)
        new_keys = []
        for each_key in keys:
            each_key = each_key.replace('%', 'pct')
            each_key = each_key.lower()
            each_key_part = each_key.split(' ')
            link = '_'
            each_key = link.join(each_key_part)
            new_keys.append(each_key)
        
        for a_row in table.findAll('tr')[1:]:
            text_all_cell = self.get_text_a_row(a_row, 'td')
            all_cell = a_row.findAll('td')
            
            lane_number = text_all_cell[index_lane]
            download_file_url = all_cell[index_download].find('a', href=True) 
             
            if lane_number != '' and len(download_file_url) == 1:
                a_lane = {}
                lane_index_now = lane_number
                
                a_lane['lane_index'] = lane_number
                a_lane['package_name'] = download_file_url.string.strip()
                a_lane['pack_data_url'] = download_file_url.get('href')
                
                all_headers = self.session_requests.get(a_lane['pack_data_url'], stream=True)
                logger.debug(f'all_headers {all_headers.headers}')
                if all_headers.status_code != 200:
                    logger.warning(f'Wrong headers {a_lane["pack_data_url"]}')
                    raise
                a_lane['http_content_length'] = all_headers.headers['content-length'] 
                lane_list.append(a_lane)
            else:
                
                if len(new_keys) != len(text_all_cell):
                    logger.warning('Different length in title and content of a table')
                else:
                    a_file = {}
                    for index in range(len(new_keys)):
                        a_file[new_keys[index]] = text_all_cell[index]
                    a_file['lane_index'] = lane_index_now
                    old_biomaterial = a_file['biomaterial']
                    new_biomaterial = old_biomaterial.replace(' ', '')
                    if len(old_biomaterial) != len(new_biomaterial):
                        logger.warning(f'Whitespace(s) in user defined name {old_biomaterial}')
                        a_file['biomaterial'] = new_biomaterial
                file_list.append(a_file)
                
        return lane_list, file_list
    
    def get_text_a_row(self, a_row, tag):
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
            a_text = self.get_text_a_cell(a_cell)
            text_list.append(a_text)
        return text_list
    
    @staticmethod
    def get_table(soup, table_id):
        """Get a table with the table_id"""
        table_id_values = table_id.split()
        if table_id_values[0] == 'table':
            table = soup.find(table_id_values[0], {table_id_values[1]: table_id_values[2]})
        else:
            a_tag = soup.find(table_id_values[0], {table_id_values[1]: table_id_values[2]})
            table = a_tag.findAll('table')[0]
        return table

    @staticmethod
    def get_text_a_cell(a_cell):
        """ Get the text in a specific cell of a table"""
        text = a_cell.findAll(text=True)
        text = [i.strip() for i in text if i not in ('\n', '')]
        if len(text) == 0:
            a_text = ''
        else:
            link = '_'
            a_text = link.join(text)
        return a_text
    
    def download_zipfile(self, url, file_path):
        """Download a zip file
        Args:
            url: link to the file
            file_path: path and file name to hold the file
        Returns:
            Date to download the file
            Time (in minutes) spend on downloading the file
            Size of the file 
        """
        time_and_size = []
        download_date = date.today().strftime('%m/%d/%Y')
        time_and_size.append(download_date)
        start = time.time()
        chunk_size = 1024 * 512
        total_size = 0
        res = self.session_requests.get(url, stream=True)
        whole_file_size = int(res.headers['content-length'])
    # print(res.headers['content-length'], real_file_size)
        limit_10_g = int(10*math.pow(1024, 3))
        if whole_file_size < limit_10_g:
            with open(file_path, 'wb') as output:
                chunk_number = 0
                for chunk in res.iter_content(chunk_size=chunk_size, decode_unicode=False):
                    if chunk:
                        total_size = total_size + chunk_size
                        chunk_number += 1
                        output.write(chunk)
            
        else:
            logger.info('HiSeq file ')
            # url_xs = url.replace('lane.fastq', 'lane_xs.fastq')
            url_xs = url
            resume_number = whole_file_size/limit_10_g + 1
            file_size = 0
            option_for_write = 'wb'
            while resume_number > 0 and file_size < whole_file_size:
                resume_number -= 1
                resume_header = {'Range': 'bytes=%d-' % file_size}
                res = self.session_requests.get(url_xs, headers=resume_header, stream=True, allow_redirects=True)
                with open(file_path, option_for_write) as output:
                    for chunk in res.iter_content(chunk_size=chunk_size, decode_unicode=False):
                        if chunk:
                            output.write(chunk)
                option_for_write = 'ab'
                time.sleep(20)
                file_size = os.stat(file_path).st_size
                logger.info(f'file size now {file_size}')
                res.close()
        end = time.time()
        time_in_min = (end - start) / 60
        time_and_size.append('%.1f' % time_in_min)
        file_size = os.stat(file_path).st_size
        time_and_size.append(str(file_size))
           
        return time_and_size
