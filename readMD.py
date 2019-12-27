import re
import json
import sys
import os
from parseJson import parse_data_structure

inAPI = False
inParameter = False
inRequest = False
inHeader = False
inBody = False
inDataStructure = False
allDataStructure = parse_data_structure()
outputJson = {
    "info": {
        "name": "",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": []
}

class ApiTemplate():
    def __init__(self, name, path, method):
        self.name = name
        self.path = path
        self.method = method
        self.parameter = []
        self.header = []
        self.body = {}
        self.isBodyArray = False
    def print_element(self):
        print([self.name, self.path, self.method, self.parameter, self.header, self.body])

def getAPI(sentence, lastApi):
    name = ""
    path = ""
    method = ""
    parameter = []
    if(sentence[0:3] == "## " and sentence.find("[") != -1):
        name, _, APIpath = sentence[3:].partition(" [")
        if(APIpath[0:1] != "/" and APIpath != ""):
            method, _, path = APIpath.partition(" ")
            path = re.split(r"({\?|\?{).*", path)[0]
            path = "{{url}}" + path.replace("{", ":").replace("}", "")
            path = path.replace("]", "")
        elif(APIpath[0:1] == "/" and APIpath != ""):
            splitUrlAndParams = re.split(r"{\?|\?{", APIpath)
            path = splitUrlAndParams[0]
            if(len(splitUrlAndParams) == 1):
                path = "{{url}}" + path.replace("{", ":").replace("}", "")
                path = path.replace("]", "")
            else:
                params = "?" + splitUrlAndParams[1].replace(",", "=123&").replace("}", "") + "=123"
                path = "{{url}}" + path.replace("{", ":").replace("}", "") + params
                path = path.replace("]", "")
    elif(sentence[0:3] == "###" and sentence.find("[") != -1):
        name, _, _ = sentence[4:].partition(" [")
        path = lastApi.path
        parameter = lastApi.parameter
        method = re.search(r"\[\w+[\] ]", sentence[3:]).group(0)
        method = re.sub(r"[^A-Z]", "", method)
    return name, path, method, parameter

def getParemeter(sentence):
    parameter = None
    if(sentence[0:1] != "+"):
        parameter = re.search(r"\`\w+\`:", sentence)
        if(parameter != None):
            parameter = parameter.group(0)
            parameter = re.sub(r"[^\w]", "", parameter)
    return parameter

def getRequestHeader(sentence):
    header = re.search(r"\w+:", sentence)
    if(header != None):
        header = header.group(0).replace(":", "")
    return header

def getRequestBody(sentence):
    body = re.search(r"\+ `(\w+)`[:| \(]", sentence)
    if(body != None):
        body = body.group(1)
    return body

typeCase = {
        "string": "",
        "array": [],
        "number": 0,
        "boolean": False,
    }

def matchType(match):
    if(match is None):
        return ""
    return typeCase.get(match.group(1), match.group(1))

def getDataStructure(sentence):
    struc = ""
    _type = ""
    if(sentence[0:3] == "## "):
        match = re.search(r"^## (\w+) \((\w+)\)", sentence)
        struc = match.group(1)
        _type = match.group(2)
        if(_type == "object"):
            dataStruc = (struc, {})
        else:
            dataStruc = (struc, "")
        allDataStructure.append(dataStruc)
    elif(re.search(r"\+ `(\w+)`", sentence) != None):
        match = re.search(r"\+ `(\w+)`", sentence)
        struc = match.group(1)
        _type = matchType(re.search(r"\((\w+)", sentence))
        (name, strucType) = allDataStructure[-1]
        if(type(strucType) == dict and re.search(r"optional\)", sentence) == None):
            strucType[struc] = _type
            allDataStructure[-1] = (name, strucType)
    return struc, _type

def findDataStruct(key):
    for name in list(allDataStructure):
        if(name == key):
            return name
    return "error_body"

## Handle the situation that document write datastructure in API's document
# def isDefalutValue(value):
#     if(value == False or value == 0 or value == "" or len(value) == 0):
#         return True
#     return False

# index = 0
# for (name, struct) in allDataStructure:
#     for key in struct:
#         if(isDefalutValue(struct[key]) is False):
#             structIndex = findDataStruct(struct[key])
#             if(type(structIndex) == int):
#                 (_, inStruct) = allDataStructure[structIndex]
#                 struct[key] = inStruct
#                 allDataStructure[index] = (name, struct)
#     index += 1

## Generate Json file
def genHeaders(headers, body):
    headerList = []
    if (body != {}):
        headerList.append({
            "key": "content-type",
            "value": "application/json"
        })
    if ("Type" in headers):
        headers.remove("Type")
    for header in headers:
        headerList.append({
            "key": header,
            "value": ""
        })
    return headerList

def genUrl(url):
    pathList = url[8:].split("/")
    path = list(filter(None, pathList))
    variable = []
    for k in path:
        if(k[0] == ":"):
            variable.append({
                "key": k[1:],
                "value": "{{" + k[1:] + "}}"
            })

    return {
        "raw": url,
        "host": "{{url}}",
        "path": path,
        "variable": variable
    }

def genBody(body):
    np = json.dumps(body, indent=2, ensure_ascii=False)
    return {
        "mode": "raw",
        "raw": np
    }

def addApi(outputFile, name, url, method, parameter, header, body):
    outputFile["item"].append({
        "name": name,
        "request": {
            "method": method,
            "header": genHeaders(header, body),
            "body": genBody(body),
            "url": genUrl(url)
        }
    })
    return outputFile

def openMultipleFiles(file_path):
    fileList = os.listdir(file_path)
    for singleFile in fileList:
        currentPath = file_path + '/' +singleFile
        if(os.path.isdir(currentPath)):
            openMultipleFiles(currentPath)
        else:
            isApiFile = re.match(r".*((_api|_apis)\.md)$", singleFile)
            if(isApiFile != None):
                f = open(currentPath, "r")
                fileName = (singleFile.split('.'))[0]
                print('start parsing ' + fileName + ': ')
                apiList = []
                apiList.append(ApiTemplate("","",""))
                inAPI = False
                inParameter = False
                inRequest = False
                inHeader = False
                inBody = False
                inDataStructure = False
                outputJson = {
                    "info": {
                        "name": fileName,
                        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
                    },
                    "item": []
                }

                for sentence in f.read().split("\n"):
                    # determine this line is in which category
                    if(sentence[0:16] == "# Data Structure"):
                        inDataStructure = True
                    if(sentence[0:2] == "##" and inDataStructure is False):
                        inAPI = True
                    elif(sentence[0:11] == "+ Parameter"):
                        inParameter = True
                    elif(sentence[0:9] == "+ Request"):
                        inRequest = True
                    elif(sentence == ""):
                        inAPI = False
                        inParameter = False

                    # after checking this line's work, then doing its job
                    if(inAPI):
                        name, path, method, parameter = getAPI(sentence, apiList[-1])
                        apiList.append(ApiTemplate(name, path, method))
                        apiList[-1].parameter = parameter
                    if(inParameter):
                        parameter = getParemeter(sentence)
                        if(parameter != None and re.search(r"optional\)", sentence) == None):
                            apiList[-1].parameter.append(parameter)
                    if(inDataStructure):
                        getDataStructure(sentence)
                    if(inRequest):
                        if(sentence[0:10] == "+ Response"):
                            inHeader = False
                            inBody = False
                            inRequest = False
                            continue
                        elif(re.search(r"\+ Header", sentence) != None):
                            inHeader = True
                            inBody = False
                        elif(re.search(r"\+ Attribute", sentence) != None):
                            if(re.search(r"\(array", sentence) != None):
                                apiList[-1].isBodyArray = True
                            inBody = True
                            inHeader = False
                            matchObj = re.search(r"[\(array\[|\(]([A-Z]\w+)", sentence)
                            if(matchObj != None):
                                apiList[-1].body = {"waitObject": matchObj.group(1)}
                                inBody = False
                        if(inHeader):
                            header = getRequestHeader(sentence)
                            if(header != None):
                                apiList[-1].header.append(header)
                        if(inBody):
                            body = getRequestBody(sentence)
                            if(body != None and re.search(r"optional\)", sentence) == None):
                                bodyObj = re.search(r"\+ .*[\(|\(array\[]([A-Z]\w+)", sentence)
                                apiList[-1].body[body] = ""
                                if(bodyObj != None):
                                    apiList[-1].body[body] = {"waitObject": bodyObj.group(1)}
                index = 0
                for api in apiList:
                    if(api.method != ""):
                        if("waitObject" in api.body):
                            structKey = findDataStruct(apiList[index].body["waitObject"])
                            req_body = allDataStructure[structKey]
                            apiList[index].body = req_body
                    index += 1
                for i in apiList:
                    if(i.method != ""):
                        outputJson = addApi(outputJson, i.name, i.path, i.method, i.parameter, i.header, i.body)

                with open(fileName +".json", "w") as fp:
                    json.dump(outputJson, fp, indent=2, ensure_ascii=False)


apiDirPath = sys.argv[1]
openMultipleFiles(apiDirPath)
