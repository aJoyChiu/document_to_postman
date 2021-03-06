import sys
import os
import re

def readAllAPIFiles(path):
  file_list = os.listdir(path)
  temp = ""
  for single_file in file_list:
    current_path = path + "/" + single_file
    if(os.path.isdir(current_path)):
      temp += readAllAPIFiles(current_path)
    else:
      # check this file is data structure file or not
      if(re.match(r".*((api|apis)\.md)$", single_file) != None):
        f = open(current_path, 'r')
        data_list = f.read().split("# Data Structures")
        if(len(data_list) >=2):
          temp = temp + data_list[1]
        f.close()
  return temp

def readAllDataFiles(path):
  files_list = os.listdir(path)
  temp = ""
  for single_file in files_list:
    current_path = path + "/" + single_file
    if(os.path.isdir(current_path)):
      temp += readAllDataFiles(current_path)
    else:
      # check this file is data structure file or not
      if(re.match(r".*_data_structures\.md$", single_file) != None):
        f = open(current_path, 'r')
        data_list = f.readlines()
        for index in range(len(data_list)):
          if(index < len(data_list)-2):
            match_object_line = re.match(r"^##.*\(object\)\n$", data_list[index])
            match_object_form = re.search(r"^\s*(-|\+).*", data_list[index+2])
            if(match_object_line != None and match_object_form == None):
              data_list.pop(index+2)
          if(index < len(data_list)):
            temp += data_list[index]
        temp = temp.replace("# Data Structures", "")
        f.close()
  return temp

data_dir_path = sys.argv[1]
all_in_one_file = "# Data Structures" + readAllDataFiles(data_dir_path)
api_dir_path = sys.argv[2]
all_in_one_file = all_in_one_file + readAllAPIFiles(api_dir_path)

f = open("temp.apib", "w")
f.write(all_in_one_file)
f.close()
