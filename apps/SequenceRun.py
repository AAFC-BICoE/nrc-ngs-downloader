class SequenceRun:

    def __init__(self, a_lane, file_info, dest_folder):
       self.data_url = a_lane[2]
       
       self.lane_info = lane_info
       self.destination_folder = dest_folder
       
    def unzip_package(self,source_name):
      if source_name.endswith("tar.gz"):
         dest_folder = source_name[:-7]
      else:
         dest_folder = source_name[:-4]

      #os.mkdir(dest_folder)
      try:
         tar = tarfile.open(source_name)
         tar.extractall(dest_folder)
         tar.close()
         os.mkdir(dest_folder)
      except Exception as e:
         print("empty file")

      path_old = "empty"
      path_new = "empty"
      if os.path.isdir(dest_folder):
         for dirpath,old_dir_name, filenames in os.walk(dest_folder):
            print(dirpath, old_dir_name, filenames)
       # if len(old_dir_name)==1:
        #   old_dir_namehere = old_dir_name[0]
             # print("old:" + old_dir_namehere)
       # print("fileName",filenames)      
        #if len(filenames)==0:
          # os.rmdir(dest_folder)       
      #   print("not a  tar.gz file:",source_name)
     # print(dirpath, old_dir_namehere, filenames)
         path_old = dirpath;
         path_new = dest_folder;
         print(path_old, path_new)
      return path_old, path_new


    def name_mapping(self,file_infos, oldname):
     # print("mapping ", oldname)
      oldname_parts = oldname.split("_")
     # print("oldname_parts", oldname_parts[0], oldname_parts[-1])
      index = 0
      for a_row in file_infos:
         if a_row[0]==oldname_parts[0]:
            newname = a_row[1]+"_"+oldname_parts[0]+"_"+oldname_parts[-1]
            fileIndex = index
         index+=1
      return oldname, newname, fileIndex


   def rename_files(self,file_infos, path_to_old_file, path_to_new_file):
      sha256_code = []
      print("pathToOldFolder", path_to_old_file)
      for dirpath,dirname, filename in os.walk(path_to_old_file):
         for a_file in filename:
            oldname, newname,fileIndex = self.name_mapping(file_infos, a_file)
            file_infos[fileIndex].append(oldname)
            file_infos[fileIndex].append(newname)
            oldname = path_to_old_file+"/"+oldname
            newname = path_to_new_file+"/"+newname
            f = open(oldname, 'rb')
            a_code = sha256(f.read()).hexdigest();
            sha256_code.append(a_code)
            print(oldname, a_code)
            os.rename(oldname, newname)
            #zip file and sha256
            file_infos[fileIndex].append(a_code)
            newnamezip = newname+".gz";
            with open(newname) as f_in, gzip.open(newnamezip, 'wb') as f_out:
               f_out.writelines(f_in)
            fileSize = os.stat(newnamezip).st_size
            file_infos[fileIndex].append(fileSize)
            os.unlink(newname)

      if os.path.isdir(path_to_old_file):
         os.rmdir(path_to_old_file)
      return sha256_code

   def remove_incomplete_data():
      
