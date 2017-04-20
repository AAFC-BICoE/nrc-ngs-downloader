import requests
import os
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

#from lxml import html
#import html
from datetime import datetime
from datetime import date
import time
#import sqlite3
from BeautifulSoup import BeautifulSoup

USERNAME = 'zhengc'
PASSWORD = 'czhen033'
URLLOGIN = 'https://lims.bioinfo.nrc.ca/login.html'
URL = 'https://lims.bioinfo.nrc.ca/lims/show_runs.html'
SEQUENCEFOLDER = "../allSequence/"

 
class parse_webpageBS:

   def login(self):
      login_data = {
         'username' : USERNAME,
         'password' : PASSWORD,
         'submit' : 'Login',
      }
      session_requests = requests.Session()
     # result = session_requests.post(URLLOGIN, data=login_data)
      result = session_requests.post(URLLOGIN, verify = False, data=login_data)

      return session_requests
    
   
   def get_package_list(self, session_requests):
      my_list = []
      r = session_requests.get(URL,verify = False)
      soup = BeautifulSoup(r.content)
      table = soup.find("table",{"class":"lims"})
      for row in table.findAll("tr"): 
         info_for_a_package = []
         for cell in row.findAll("td"):
            cell_link = cell.find('a', href = True)
            if cell_link is not None:
                info_for_a_package.append(cell_link.get('href'))
            for a_text in cell.findAll(text=True):
                info_for_a_package.append(a_text.strip()) 
         info_for_a_package = [i for i in info_for_a_package if i != '']
         my_list.append(info_for_a_package)
     # print(my_list)
      return my_list   
   
   def download(self, pack_info_url, pathToFolder):
      more_info = [pack_info_url,date.today().strftime('%m/%d/%Y'),]
      session_requests=self.login()
      r = session_requests.get(pack_info_url, verify = False)
      soup = BeautifulSoup(r.content)
      table = soup.find("table",{"class":"label_value"})
      for row in table.findAll("tr"):
         two_text = row.findAll(text = True)
         two_text = [i for i in two_text if i != '\n']  
        # print(len(two_text), two_text)
         more_info.append(two_text[1].strip())
         #for cell in row.findAll("td"):
         #   for a_text in cell.findAll(text=True):
         #      more_info.append(a_text.strip())
      tabledf = soup.find("table",{"class":"lims"})
      secondrow = tabledf.findAll("tr")[1]
     # print(secondrow)
      #print("lims table", len(tabledf))
      all_link = secondrow.findAll('a', href = True)
      for a_link in all_link:
        # print("alink", a_link)
         if a_link is not None:
            pack_data_url = a_link.get('href')
            pack_name = a_link.string.strip()
            print(pack_name, pack_data_url)
            more_info.append(pack_name)
            more_info.append(pack_data_url)
            pack_path_and_name = pathToFolder+pack_name
            time_and_size = self.download_package(pack_data_url,pack_path_and_name, session_requests)
            more_info.append(time_and_size)
            #for a_text in cell.findAll(text=True):

      return more_info

   def download_package(self,urlAddress, outputFileName, session_requests):
      time_and_size = []
      start = time.time()
      chunkSize = 4096*512*16
      totalSize = 0
      res = session_requests.get(urlAddress, stream=True)
      with open(outputFileName, 'wb') as output:
         chunknumber = 0
         for chunk in res.iter_content(chunk_size=chunkSize, decode_unicode=False):
            if chunk:
               totalSize = totalSize +chunkSize 
               chunknumber += 1
               output.write(chunk)
               print(datetime.now(), totalSize)
      end = time.time()
      time_in_min = (end-start)/60
     # time_and_size.append(str(datetime.timedelta(seconds = time_in_sec)))
      print("time in min: ", time_in_min)
      time_and_size.append(time_in_min.float128(1))
      fileSize = os.stat(outputFileName).st_size
      time_and_size.append(fileSize)
      print(time_in_sec, totalSize,fileSize )
      return time_and_size     

from parse_webpageBS import parse_webpageBS

def main():
   my_parser = parse_webpageBS()
   session_request = my_parser.login()
   my_parser.get_package_list(session_request)

if __name__ == "__main__":
   main()
