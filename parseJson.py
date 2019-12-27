import json
import re

def loadDict(_dict, indexName, index = None):
    if(index is None):
        if(type(_dict) is list):
            return _dict[0][indexName]
        elif(type(_dict) is dict):
            return _dict[indexName]
    elif(type(index) is int):
        if(type(_dict) is list):
            return _dict[0][indexName]
        elif(type(_dict) is dict):
            return _dict[indexName]
    return _dict

def readData(_list):
    temp = {}
    for b in _list:
        if 'content' in b:
            b = b['content']
            if(type(b) == list):
                inside = readData(b)
                temp = inside
            elif(type(b) == dict):
                key = b["key"]['content']
                value = b["value"].get('content', "object_" + b["value"]["element"])
                isList = b["value"]["element"] == "array"
                if(type(value) == list):
                    inside = readData(value)
                    if(isList):
                        temp[key] = [inside]
                    else:
                        temp[key] = inside
                else:
                    temp[key] = value
    return temp

def parse_data_structure():
    name = ""
    f = open("save_by_drafter.json")
    originData = json.load(f)
    final = {}
    dataStructures = {}

    originData = loadDict(originData, 'content')
    originData = loadDict(originData, 'content')
    originData = loadDict(originData, 'content')

    for struc in originData:
        struc = struc['content']
        name = struc["meta"]["id"]['content']
        if(struc["element"] == "enum"):
            continue
        elif(struc["element"] != "object"):
            name = name + "_object_" + struc["element"]
        struc = struc['content']
        for b in struc:
            if(b["element"] == "select"):
                b =b['content'][0]['content'][0]
            b = b['content']
            key = b["key"]['content']
            value = b["value"].get('content', "object_" + b["value"]["element"])
            if(b["value"]["element"] == "enum"):
                value = b["value"]["attributes"]["enumerations"]['content'][0]['content']
            elif(b["value"]["element"] == "array" and 'content' in b["value"]):
                value = b["value"]['content'][0].get('content', "object_" + b["value"]['content'][0]["element"])
            isList = b["value"]["element"] == "array"
            if(type(value) == list):
                inside = readData(value)
                if(isList):
                    final[key] = [inside]
                else:
                    final[key] = inside
            else:
                if(isList):
                    final[key] = [value]
                else:
                    final[key] = value
        dataStructures[name] = final
        final = {}

    for datastruc in list(dataStructures):
        if(datastruc.find("_object_") != -1):
            name = re.sub(r"_object_.*", "", datastruc)
            for strucName in list(dataStructures):
                if(strucName.find(re.sub(r".*_object_", "", datastruc) + "_object_") == 0):
                    dataStructures = replaceObj(strucName, dataStructures)
            if(datastruc in dataStructures):
                dataStructures[name] = {**dataStructures[datastruc], **dataStructures[re.sub(r".*_object_", "", datastruc)]}
                dataStructures.pop(datastruc)
            datastruc = name
        struc = dataStructures[datastruc]
        for index in struc:
            if(type(struc[index]) == dict):
                dataStructures[datastruc][index] = findObject(struc[index], dataStructures)
            elif(type(struc[index]) == list and type(struc[index][0]) == str):
                isObject = struc[index][0].find("object_")
                if(isObject != -1):
                    objName = struc[index][0].replace("object_", "")
                    dataStructures[datastruc][index][0] = dataStructures.get(objName, "object=>" + objName)
            elif(type(struc[index]) == str):
                isObject = struc[index].find("object_")
                if(isObject != -1):
                    objName = struc[index].replace("object_", "")
                    dataStructures[datastruc][index] = dataStructures.get(objName, "object=>" + objName)

    return dataStructures

def replaceObj(datastruc, dataStructures):
    if(datastruc.find("_object_") != -1):
        name = re.sub(r"_object_.*", "", datastruc)
        for strucName in dataStructures:
            if(strucName.find(re.sub(r".*_object_", "", datastruc) + "_object_") == 0):
                dataStructures = replaceObj(strucName, dataStructures)
        dataStructures[name] = {**dataStructures[datastruc], **dataStructures[re.sub(r".*_object_", "", datastruc)]}
        dataStructures.pop(datastruc)
        datastruc = name
    return dataStructures

def findObject(struc, dataStructures):
    for index in struc:
        if(type(struc[index]) == dict):
            struc[index] = findObject(struc[index], dataStructures)
        elif(type(struc[index]) == list and type(struc[index][0]) == str):
            isObject = struc[index][0].find("object_")
            if(isObject != -1):
                objName = struc[index][0].replace("object_", "")
                struc[index][0] = dataStructures.get(objName, "object=>" + objName)
        elif(type(struc[index]) == str):
            isObject = struc[index].find("object_")
            if(isObject != -1):
                objName = struc[index].replace("object_", "")
                struc[index] = dataStructures.get(objName, "object=>" + objName)
    return struc

## If only run this file, run the function below
# parse_data_structure()
