import os
import sys
import re

def read_all_files(path):
  files_list = os.listdir(path)
  temp = ""
  for single_file in files_list:
    curren_path = path + "/" + single_file
    if(os.path.isdir(curren_path)):
      temp += read_all_files(curren_path)
    else:
      # check this file is data structure file or not
      if(re.match(r".*_data_structures\.md$", single_file) != None):
        f = open(curren_path, 'r')
        data_list = f.readlines()
        for index in range(len(data_list)):
          if(index < len(data_list)-2):
            if(re.match(r"^\##.*\(object\)\n", data_list[index]) != None and re.search(r"^\s*(-|\+).*", data_list[index+2]) == None):
              data_list.pop(index+2)
          if(index < len(data_list)):
            temp += data_list[index]
        temp = temp.replace("# Data Structures", "")
        f.close()
  return temp

# document_path = sys.argv[1]
data_dir_path = sys.argv[1]
all_in_one_file = "# Data Structures" + read_all_files(data_dir_path)

f = open("temp.apib", "w")
f.write(all_in_one_file)
f.close()
