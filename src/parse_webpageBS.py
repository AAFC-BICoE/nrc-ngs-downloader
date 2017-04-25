import requests
import os
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import tarfile
import gzip
from datetime import datetime
from datetime import date
import time
from BeautifulSoup import BeautifulSoup
from hashlib import sha256
import functools

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
      return my_list   
   
   def get_pack_info(self, pack_info_url, soup):
      pack_info = [pack_info_url,date.today().strftime('%m/%d/%Y'),]
      table = soup.find("table",{"class":"label_value"})
      for row in table.findAll("tr"):
         two_text = row.findAll(text = True)
         two_text = [i for i in two_text if i != '\n']
         pack_info.append(two_text[1].strip())
      tabledf = soup.find("table",{"class":"lims"})
      secondrow = tabledf.findAll("tr")[1]
      all_link = secondrow.findAll('a', href = True)
      for a_link in all_link:
         if a_link is not None:
            pack_data_url = a_link.get('href')
            pack_name = a_link.string.strip()
            print(pack_name, pack_data_url)
            pack_info.append(pack_name)
            pack_info.append(pack_data_url)
      return pack_info
 
   def action_for_a_package(self, pack_info_url, pathToFolder, pathDestin):
      session_requests=self.login()
      r = session_requests.get(pack_info_url, verify = False)
      soup = BeautifulSoup(r.content)

      package_info = self.get_pack_info(pack_info_url,soup)
      pack_data_url = package_info[-1]
      pack_name = package_info[-2]

      file_infos = self.get_file_list(soup)

      pack_path_and_name = pathToFolder+pack_name
      #time_and_size = self.download_package(pack_data_url,pack_path_and_name, session_requests)
      #package_info.append(time_and_size[0])
      #package_info.append(time_and_size[1])
      
      path_to_old_file, path_to_new_file =  self.unzip_package(pack_path_and_name)
      self.rename_files(file_infos, path_to_old_file, path_to_new_file)
      
      return package_info, file_infos

   def rename_files(self,file_infos, path_to_old_file, path_to_new_file):
      sha256_code = []
      for dirpath,dirname, filename in os.walk(path_to_old_file):
         for a_file in filename:
            oldname, newname = self.name_mapping(file_infos, a_file)
            oldname = path_to_old_file+"/"+oldname
            newname = path_to_new_file+"/"+newname
           # print(a_file,"two names:", oldname, newname)
            #digest = hashlib.sha256()
            f = open(oldname, 'rb')
            a_code = sha256(f.read()).hexdigest();
            sha256_code.append(a_code)
            print(oldname, a_code)
            os.rename(oldname, newname)
            #zip file and sha256
            
            newnamezip = newname+".gz";
            with open(newname) as f_in, gzip.open(newnamezip, 'wb') as f_out:
               f_out.writelines(f_in)
            os.unlink(newname)
      os.rmdir(path_to_old_file)
      return sha256_code
            
   def name_mapping(self,file_infos, oldname):
     # print("mapping ", oldname)
      oldname_parts = oldname.split("_")
     # print("oldname_parts", oldname_parts[0], oldname_parts[-1])
      for a_row in file_infos:
         if a_row[0]==oldname_parts[0]:
            newname = a_row[1]+"_"+oldname_parts[0]+"_"+oldname_parts[-1]
      return oldname, newname

   def unzip_package(self,source_name):
      if source_name.endswith("tar.gz"):
         dest_folder = source_name[:-7]
         os.mkdir(dest_folder)
         tar = tarfile.open(source_name)
         tar.extractall(dest_folder)
         tar.close()
         for dirpath,old_dir_name, filenames in os.walk(dest_folder):
          # print(dirpath, old_dir_name, filenames)
           if len(old_dir_name)==1:
              old_dir_namehere = old_dir_name[0]
             # print("old:" + old_dir_namehere)      
      else:
         print("not a  tar.gz file:",source_name)
     # print(dirpath, old_dir_namehere, filenames)
      path_old = dirpath;
      path_new = dest_folder;
      print(path_old, path_new)
      return path_old, path_new

   def get_file_list(self, soup):
      file_list = []
      tabledf = soup.find("table",{"class":"lims"})
      all_row_for_files = tabledf.findAll("tr")[2:]
      for a_row in all_row_for_files:
         a_file_info = a_row.findAll(text=True)
         a_file_info2 = []
         for a_item in a_file_info:
            a_file_info2.append(a_item.strip())
         a_file_info2 = [i for i in a_file_info2 if i not in ('\n','')]
         file_list.append(a_file_info2)
      return file_list

   def download_package(self,urlAddress, outputFileName, session_requests):
      time_and_size = []
      start = time.time()
      chunkSize = 4096*512*4
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
           # if chunknumber==5:
            #   break; 
      end = time.time()
      time_in_min = (end-start)/60
      time_and_size.append("%.1f" % time_in_min)
      fileSize = os.stat(outputFileName).st_size
      time_and_size.append(fileSize)
      return time_and_size     

"""
from parse_webpageBS import parse_webpageBS

def main():
   my_parser = parse_webpageBS()
   session_request = my_parser.login()
   my_parser.get_package_list(session_request)

if __name__ == "__main__":
   main()
"""
