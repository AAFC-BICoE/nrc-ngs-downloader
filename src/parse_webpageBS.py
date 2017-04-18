import requests
#from lxml import html
#import html
from datetime import datetime
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
      print(my_list)
      return my_list


"""    
   def parse_info_data_files():

   def parse_info_data_packages(tree, c):
      runName = tree.xpath('//table[@class="lims"]/tbody/tr/td[1]$
      runName = [word.strip() for word in runName]
      runNameLinks = tree.xpath('//table[@class="lims"]/tbody/tr/$
      plateName = tree.xpath('//table[@class="lims"]/tbody/tr/td[$
      platform = tree.xpath('//table[@class="lims"]/tbody/tr/td[3$
      operator = tree.xpath('//table[@class="lims"]/tbody/tr/td[4$
      creationDate = tree.xpath('//table[@class="lims"]/tbody/tr/$
      description = tree.xpath('//table[@class="lims"]/tbody/tr/t$
      status = tree.xpath('//table[@class="lims"]/tbody/tr/td[7]/$
      c.execute("INSERT INTO {} ")
   

   def download(urlAddress, outputFileName, chunkSize, session_requests):
      res = session_requests.get(urlAddress, stream=True)
      with open(outputFileName, 'wb') as output:
         chunknumber = 0
         for chunk in res.iter_content(chunk_size=chunkSize, decode_unicode=False):
            if chunk:
               chunknumber += 1
               output.write(chunk)
               print(datetime.now())


"""


from parse_webpageBS import parse_webpageBS

def main():
   my_parser = parse_webpageBS()
   session_request = my_parser.login()
   my_parser.get_package_list(session_request)

if __name__ == "__main__":
   main()
