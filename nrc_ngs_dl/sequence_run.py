import os
import logging
import shutil
import tarfile
import gzip
from hashlib import sha256

logger  = logging.getLogger('nrc_ngs_dl.sequence_run')
class SequenceRun:
    def __init__(self, a_lane, file_info, dest_folder):
        self.data_url = a_lane[2]
        self.file_info = file_info
        self.file_info[0].append('new_name')
        self.file_info[0].append('original_name')
        self.file_info[0].append('file_size')
        self.file_info[0].append('folder_name')
        self.file_info[0].append('SHA256')
        self.path_source_file = os.path.join(dest_folder,a_lane[1])
        self.path_destination_folder = os.path.join(dest_folder,a_lane[1].split('.')[0])
        if os.path.exists(self.path_destination_folder):
            logger.info('Delete folder for broken/reprocessed data')
            shutil.rmtree(self.path_destination_folder)
        os.mkdir(self.path_destination_folder)
       
    def unzip_package(self):
        try:
            logger.info('Unzip file ...')
            tar = tarfile.open(self.path_source_file)
            tar.extractall(self.path_destination_folder)
            tar.close()
        except:
            logger.info("An empty .tar/.tar.gz file")
            return False
        return True

    def name_mapping(self,oldname):
        #print("mapping old name", oldname)
        oldname_parts = oldname.split("_")
        # print("oldname_parts", oldname_parts[0], oldname_parts[-1])
        index = 0
        for a_row in self.file_info:
            if a_row[1]==oldname_parts[0]:
                newname = a_row[2]+"_"+oldname_parts[0]+"_"+oldname_parts[-1]
                fileIndex = index
            index+=1
        if newname is None:
            logger.info('cannot find matching file in file list')
            newname = oldname    
        return oldname, newname, fileIndex


    def rename_files(self):
        #print(self.file_info)
        logger.info('Rename files ...')
        path_to_old_file = self.path_destination_folder
        for dirpath, dirname,filename in os.walk(self.path_destination_folder):
            if len(dirname) ==1:
                #path_to_old_file = dirpath+"/"+dirname[0]
                path_to_old_file = os.path.join(dirpath,dirname[0])
            
        for dirpath, dirname,filename in os.walk(path_to_old_file):
            for a_file in filename:
                oldname_short, newname_short,fileIndex = self.name_mapping(a_file)
                if oldname_short == newname_short:
                    logger.info("Cannot find matching name %s" % (a_file))
                
                oldname = os.path.join(path_to_old_file, oldname_short)
                newname = os.path.join(self.path_destination_folder, newname_short)
                
                f = open(oldname, 'rb')
                a_code = sha256(f.read()).hexdigest();
                os.rename(oldname, newname)
                    #zip file and sha256
                
                newnamezip = newname+".gz";
                with open(newname) as f_in, gzip.open(newnamezip, 'wb') as f_out:
                    f_out.writelines(f_in)
                
                if len(self.file_info[0]) == len(self.file_info[fileIndex]):
                    #create a new row by coping file_info[fileIndex]
                    last_index = len(self.file_info)
                    new_row = []
                    index = 0
                    while index < len(self.file_info[fileIndex])-5 :
                        new_row.append(self.file_info[fileIndex][index])
                        index+=1
                    self.file_info.append(new_row)   
                    fileIndex = last_index
                    
                self.file_info[fileIndex].append(newname_short)
                self.file_info[fileIndex].append(oldname_short)   
                fileSize = os.stat(newname).st_size
                self.file_info[fileIndex].append(str(fileSize))
                os.unlink(newname)
                self.file_info[fileIndex].append(self.path_destination_folder)
                self.file_info[fileIndex].append(a_code)

        if os.path.isdir(path_to_old_file):
            os.rmdir(path_to_old_file)

    def remove_incomplete_data(self, file_name):
        logger.info('Remove incomplete data')
        if os.path.isfile(file_name):
            os.remove(file_name)
        if os.path.isdir(file_name):
            shutil.rmtree(file_name)
        
      
