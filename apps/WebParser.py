import requests
import os
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from datetime import datetime
from datetime import date
import time
from BeautifulSoup import BeautifulSoup

#import functools

 
class WebParser:
    def __init__(self, login_url, runlist_url, username, password):
        login_data = {
            'username' : username,
            'password' : password,
            'submit' : 'Login',
            }
        session_requests = requests.Session()
        session_requests.post(login_url, verify=False, data=login_data)
        self.session_requests = session_requests
        self.runlist_url = runlist_url
    
    def get_runlist(self):
        packages = []
        r = self.session_requests.get(self.runlist_url, verify=False)
        soup = BeautifulSoup(r.content)
        table = soup.find("table", {"class":"lims"})
        for row in table.findAll("tr"):
            info_for_a_package = []
            for cell in row.findAll("td"):
                cell_link = cell.find('a', href=True)
                if cell_link is not None:
                    info_for_a_package.append(cell_link.get('href'))
                for a_text in cell.findAll(text=True):
                    info_for_a_package.append(a_text.strip()) 
                    info_for_a_package = [i for i in info_for_a_package if i != '']
            if len(info_for_a_package) != 0 and info_for_a_package[-1] == "completed":
                packages.append(info_for_a_package) 
        reverse_list = list(reversed(packages))
        return reverse_list
    
    def get_runinfo(self, run_url):
        r = self.session_requests.get(run_url, verify=False)
        soup = BeautifulSoup(r.content)
        run_info = {}
        table = soup.find("table", {"class":"label_value"})
        for row in table.findAll("tr"):
            two_text = row.findAll(text=True)
            two_text = [i for i in two_text if i != '\n']
            column_name = two_text[0].strip()
            column_value = two_text[1].strip()
            column_name = column_name.lower()
            column_name_part = column_name.split(" ")
            link = "_"
            column_name = link.join(column_name_part)[:-1]
            run_info[column_name] = column_value
        return run_info
        
    def get_laneinfo(self, run_url):
        r = self.session_requests.get(run_url, verify=False)
        soup = BeautifulSoup(r.content)
        table = soup.find("table", {"class":"lims"})
        title_row = table.findAll("tr")[0]
        keys = self.get_text_arow(title_row,"th")
        index_lane = keys.index("Lane")
        index_download = keys.index("Download")
        lane_list = []
        row_index = 1
        for a_row in table.findAll("tr")[1:]:
            row_index += 1
            a_lane = []
            #a_line = self.get_text_arow(a_row,"td")
            all_cell = a_row.findAll("td")
            lane_number = all_cell[index_lane].findAll(text = True)[0].strip()
            #download_file_name = all_cell[index_download].findAll(text = True)
            #download_file_name = [i for i in download_file_name if i != '\n']
            download_file_url = all_cell[index_download].find('a', href=True)  
            #pack_data_url = a_link.get('href')
            #pack_name = a_link.string.strip()
            if lane_number != "" and len(download_file_url) == 1:
                previous_lane_end = row_index-2
                if previous_lane_end > 0:
                    lane_list[len(lane_list)-1].append(previous_lane_end)
                a_lane.append(lane_number)
                a_lane.append(download_file_url.string.strip())
                a_lane.append(download_file_url.get('href'))
                
                #check header of a_lane[2]
                #all_headers = self.session_requests.head(a_lane[2])
                all_headers = self.session_requests.get(a_lane[2], stream=True)
                if all_headers.status_code != 200:
                    print("wrong headers")
                #print(all_headers.status_code)
                #if all_headers.status_code != 200:
                    #all_headers = self.session_requests.get(a_lane[2], stream=True)
                print(all_headers.status_code)
                content_length = all_headers.headers['content-length']
                print(a_lane[2], all_headers.headers)
                a_lane.append(content_length)
                a_lane.append((row_index))  #start of a lane
            if len(a_lane) > 3:
                lane_list.append(a_lane)
        lane_list[len(lane_list)-1].append(row_index-1)
        return lane_list
    
    def get_fileinfo(self, run_url, a_lane_info):
        file_list = []
        r = self.session_requests.get(run_url, verify=False)
        soup = BeautifulSoup(r.content)
        table = soup.find("table", {"class":"lims"})
        title_row = table.findAll("tr")[0]
        keys = self.get_text_arow(title_row,"th")
        new_keys=[]
        for each_key in keys:
            each_key = each_key.replace("%", "pct")
            each_key = each_key.lower()
            each_key_part = each_key.split(" ")
            link = "_"
            each_key = link.join(each_key_part)
            new_keys.append(each_key)
        file_list.append(new_keys)
        lane_start = a_lane_info[4]
        lane_end = a_lane_info[5]+1
        for a_row in table.findAll("tr")[lane_start:lane_end]:
            text_all_cell = self.get_text_arow(a_row,"td")
            file_list.append(text_all_cell)     
        return file_list
    
    def get_text_arow(self,a_row, tag):
        text_list = []
        all_cell = a_row.findAll(tag)
        for a_cell in all_cell:
            a_text = a_cell.findAll(text = True)
            a_text = [i for i in a_text if i not in ("\n", "")]
            if len(a_text) == 0:
                text_list.append("")
            else:
                text_list.append(a_text[0].strip())
        return text_list
    
    def download_zipfile(self, urlAddress, outputFileName):
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
                # if chunknumber==5:
                #    break;
        end = time.time()
        time_in_min = (end - start) / 60
        time_and_size.append("%.1f" % time_in_min)
        fileSize = os.stat(outputFileName).st_size
        time_and_size.append(str(fileSize))
        return time_and_size
        
        



