import os
import copy
import logging
import shutil
import tarfile
import gzip
from hashlib import sha256

logger = logging.getLogger('nrc_ngs_dl.sequence_run')


class SequenceRun:
    def __init__(self, a_lane, run_name, file_info, dest_folder, folder_mode, file_mode):
        """Initialize the object 
        Args:
            a_lane: information of a lane
            file_info: information of all the files in this lane
            dest_folder: the folder to keep all the fastq files of this lane
        """
        self.data_url = a_lane['pack_data_url']
        self.file_info = file_info
        self.path_source_file = os.path.join(dest_folder, a_lane['package_name'])
        self.path_destination_folder = os.path.join(dest_folder, run_name)
        if os.path.exists(self.path_destination_folder):
            logger.info(f'Delete folder for broken/reprocessed data {self.path_destination_folder}')
            shutil.rmtree(self.path_destination_folder)
        os.mkdir(self.path_destination_folder)
        os.chmod(self.path_destination_folder, int(folder_mode, 8))
        self.file_mode = int(file_mode, 8)
       
    def unzip_package(self, file_size, http_content_length):
        """Unzip a .tar or .tar.gz file"""
        if http_content_length != file_size:
            logger.warning(f'downloaded file size {file_size} is different with the '
                           f'http_content_length {http_content_length}')
            os.unlink(self.path_source_file)
            return False
        try:
            logger.info(f'Unzip file {self.path_source_file}')
            tar = tarfile.open(self.path_source_file)
            tar.extractall(self.path_destination_folder)
            tar.close()
            os.unlink(self.path_source_file)
        except:
            if os.path.exists(self.path_destination_folder):
                shutil.rmtree(self.path_destination_folder)
            logger.warning("An empty/incomplete .tar/.tar.gz file")
            os.unlink(self.path_source_file)
            return False
        return True

    def name_mapping(self, old_name):
        """Find the correspondent new name for a file by searching the list of file information"""
        old_name_parts = old_name.split("_")
        index = 0
        last_part = old_name_parts[-1]
        newname = ''
        file_index = -1
        if old_name_parts[-1] == 'r1.fastq.gz':
            last_part = 'R1.fq.gz'
        if old_name_parts[-1] == 'r2.fastq.gz':
            last_part = 'R2.fq.gz'
        for a_row in self.file_info:
            if a_row['sample_name'] == old_name_parts[0]:
                newname = a_row['biomaterial']+"_"+old_name_parts[0]+"_"+last_part
                file_index = index
            index += 1
        if newname == '':
            logger.warning(f'cannot find matching name {old_name}')
            newname = old_name + '_old_name'
        logger.debug(f'old_name {old_name} and new_name {newname}')
        return old_name, newname, file_index

    def rename_a_file(self, a_file, a_path):
        """Rename a file in a lane with a new name"""
    
        old_name_short, newname_short, file_index = self.name_mapping(a_file)
        old_name = os.path.join(a_path, old_name_short)
        newname = os.path.join(self.path_destination_folder, newname_short)
        f = open(old_name, 'rb')
        a_code = sha256(f.read()).hexdigest()
        os.rename(old_name, newname)
        os.chmod(newname, self.file_mode)
        # zip file and sha256
        if not newname.endswith('.gz'):
            newname_short = newname_short + '.gz'
            newnamezip = newname + '.gz'
            with open(newname, 'rb') as f_in, gzip.open(newnamezip, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            f_zip = open(newnamezip, 'rb')
            a_code = sha256(f_zip.read()).hexdigest()
            os.chmod(newnamezip, self.file_mode)
                
        # if self.file_info[file_index] has old name, new name. sha256
        if 'new_name' in self.file_info[file_index]:
            new_row = copy.deepcopy(self.file_info[file_index])
            file_index = len(self.file_info)
            self.file_info.append(new_row)
                    
        self.file_info[file_index]['original_name'] = old_name_short
        self.file_info[file_index]['new_name'] = newname_short
        self.file_info[file_index]['folder_name'] = self.path_destination_folder
        self.file_info[file_index]['SHA256'] = a_code
        self.file_info[file_index]['file_size'] = os.stat(newname).st_size
        if not newname.endswith('.gz'):
            os.unlink(newname)

    def rename_files(self):
        """Rename files in a lane with new names"""
        logger.info('Rename files <User defined name>_<Sample name>_(R1/R2).fq.gz')
        
        for dirpath, dirname, filename in os.walk(self.path_destination_folder):
            if dirpath.endswith('.failed'):
                shutil.rmtree(dirpath, ignore_errors=True)
                logger.info(f'Remove folder {dirpath}')
        
        for dirpath, dirname, filename in os.walk(self.path_destination_folder):
            for a_file in filename:
                self.rename_a_file(a_file, dirpath)
                '''
                #check if the file is a sequence file or not
                if a_file.str.contains('.fq|.fastq|.fasta|.fna|.ffn|.faa|.frn'):
                    self.rename_a_file(a_file, dirpath)
                else:
                    non_sequence_file = os.path.join(dirpath, a_file)
                    os.unlink(a_file)
                    logger.warning('Remove a non-sequence file %s' % (a_file))
                '''
        for dirpath, dirname, filename in os.walk(self.path_destination_folder):
            if dirpath != self.path_destination_folder:
                os.rmdir(dirpath)

        
      
