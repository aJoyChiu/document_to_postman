import sys
import os
import re

def readAllFiles(path):
  file_list = os.listdir(path)
  temp = ""
  for single_file in file_list:
    current_path = path + "/" + single_file
    if(os.path.isdir(current_path)):
      temp += readAllFiles(current_path)
    else:
      # check this file is data structure file or not
      if(re.match(r".*((api|apis)\.md)$", single_file) != None):
        f = open(current_path, 'r')
        data_list = f.read().split("# Data Structures")[1]
        temp = temp + data_list
        f.close()
  return temp


api_dir_path = sys.argv[1]
all_in_one_file = "# Data Structures\n" + readAllFiles(api_dir_path)

f = open("temp.apib", "w")
f.write(all_in_one_file)
f.close()
