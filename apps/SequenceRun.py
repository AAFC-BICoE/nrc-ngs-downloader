import os
import tarfile
import gzip
from hashlib import sha256

class SequenceRun:
    def __init__(self, a_lane, file_info, dest_folder):
        self.data_url = a_lane[2]
        self.file_info = file_info
        self.file_info[0].append('new_name')
        self.file_info[0].append('original_name')
        self.file_info[0].append('file_size')
        self.file_info[0].append('folder_name')
        self.file_info[0].append('SHA256')
        self.path_source_file = dest_folder+a_lane[1]
        self.path_destination_folder = dest_folder+a_lane[1].split('.')[0]
        #if os.path.isdir(self.destination_folder):
        os.mkdir(self.path_destination_folder)
        print(self.data_url)
        print(self.path_source_file)
        print(self.path_destination_folder)
       
    def unzip_package(self):
        try:
            tar = tarfile.open(self.path_source_file)
            tar.extractall(self.path_destination_folder)
            tar.close()
        except Exception as e:
            print("empty file")
            return False
        return True

    def name_mapping(self,oldname):
        # print("mapping ", oldname)
        oldname_parts = oldname.split("_")
        # print("oldname_parts", oldname_parts[0], oldname_parts[-1])
        index = 0
        for a_row in self.file_info:
            if a_row[1]==oldname_parts[0]:
                newname = a_row[2]+"_"+oldname_parts[0]+"_"+oldname_parts[-1]
                fileIndex = index
            index+=1     
        return oldname, newname, fileIndex


    def rename_files(self):
        path_to_old_file = self.path_destination_folder
        for dirpath, dirname,filename in os.walk(self.path_destination_folder):
            if len(dirname) ==1:
                path_to_old_file = dirname[0]
        
        print(path_to_old_file)      
        for dirpath, dirname,filename in os.walk(path_to_old_file):
            for a_file in filename:
                oldname, newname,fileIndex = self.name_mapping(a_file)
                self.file_info[fileIndex].append(newname)
                self.file_info[fileIndex].append(oldname)
                oldname = path_to_old_file+"/"+oldname
                newname = self.path_destination_folder+"/"+newname
                
                f = open(oldname, 'rb')
                a_code = sha256(f.read()).hexdigest();
                os.rename(oldname, newname)
                #zip file and sha256
                
                newnamezip = newname+".gz";
                with open(newname) as f_in, gzip.open(newnamezip, 'wb') as f_out:
                    f_out.writelines(f_in)
                    fileSize = os.stat(newnamezip).st_size
                    self.file_info[fileIndex].append(fileSize)
                    os.unlink(newname)
                self.file_info[fileIndex].append(self.path_destination_folder)
                self.file_info[fileIndex].append(a_code)

        if os.path.isdir(path_to_old_file):
            os.rmdir(path_to_old_file)

    def remove_incomplete_data(self):
        print('remove incomplete data')
      
