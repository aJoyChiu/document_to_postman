import re
import json
import sys
from parseJson import parse_data_structure

inAPI = False
inParameter = False
inRequest = False
inHeader = False
inBody = False
inDataStructure = False

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
        print([self.name, self.path, self.method, self.header, self.body])

def getAPI(setence, lastApi):
    name = ""
    path = ""
    method = ""
    parameter = []
    if(setence[0:3] == "## " and setence.find("[") != -1):
        name, _, APIpath = setence[3:].partition(" [")
        if(APIpath[0:1] != "/" and APIpath != ""):
            method, _, path = APIpath.partition(" ")
            path = re.split(r"({\?|\?{).*", path)[0]
            path = "{{url}}" + path.replace("{", ":").replace("}", "")
            path = path.replace("]", "")
        elif(APIpath[0:1] == "/" and APIpath != ""):
            path = re.split(r"({\?|\?{).*", APIpath[1:])[0]
            path = "{{url}}/" + path.replace("{", ":").replace("}", "")
            path = path.replace("]", "")
    elif(setence[0:3] == "###" and setence.find("[") != -1):
        name, _, _ = setence[4:].partition(" [")
        path = lastApi.path
        parameter = lastApi.parameter
        method = re.search(r"\[\w+[\] ]", setence[3:]).group(0)
        method = re.sub(r"[^A-Z]", "", method)
    return name, path, method, parameter

def getParemeter(setence):
    parameter = None
    if(setence[0:1] != "+"):
        parameter = re.search(r"\`\w+\`:", setence)
        if(parameter != None):
            parameter = parameter.group(0)
            parameter = re.sub(r"[^\w]", "", parameter)
    return parameter

def getRequestHeader(setence):
    header = re.search(r"\w+:", setence)
    if(header != None):
        header = header.group(0).replace(":", "")
    return header

def getRequestBody(setence):
    body = re.search(r"\+ `(\w+)`[:| \(]", setence)
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

file_name = ((sys.argv[1].split('/'))[-1].split('.'))[0]
file_path = sys.argv[1]
f = open(file_path, "r")
dataStrucList = parse_data_structure()
# print(dataStrucList)
apiList = list()
apiList.append(ApiTemplate("","",""))
txt = {
    "info": {
        "name": file_name,
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": []
}

def getDataStructure(setence):
    struc = ""
    _type = ""
    if(setence[0:3] == "## "):
        match = re.search(r"^## (\w+) \((\w+)\)", setence)
        struc = match.group(1)
        _type = match.group(2)
        if(_type == "object"):
            dataStruc = (struc, {})
        else:
            dataStruc = (struc, "")
        dataStrucList.append(dataStruc)
    elif(re.search(r"\+ `(\w+)`", setence) != None):
        match = re.search(r"\+ `(\w+)`", setence)
        struc = match.group(1)
        _type = matchType(re.search(r"\((\w+)", setence))
        (name, strucType) = dataStrucList[-1]
        if(type(strucType) == dict and re.search(r"optional\)", setence) == None):
            strucType[struc] = _type
            dataStrucList[-1] = (name, strucType)
    return struc, _type

for setence in f.read().split("\n"):
    # determine this line is in which category
    if(setence[0:16] == "# Data Structure"):
        inDataStructure = True
    if(setence[0:2] == "##" and inDataStructure is False):
        inAPI = True
    elif(setence[0:11] == "+ Parameter"):
        inParameter = True
    elif(setence[0:9] == "+ Request"):
        inRequest = True
    elif(setence == ""):
        inAPI = False
        inParameter = False

    # after checking this line's work, then doing its job
    if(inAPI):
        name, path, method, parameter = getAPI(setence, apiList[-1])
        apiList.append(ApiTemplate(name, path, method))
        apiList[-1].parameter = parameter
    if(inParameter):
        parameter = getParemeter(setence)
        if(parameter != None and re.search(r"optional\)", setence) == None):
            apiList[-1].parameter.append(parameter)
    if(inDataStructure):
        getDataStructure(setence)
    if(inRequest):
        if(setence[0:10] == "+ Response"):
            inHeader = False
            inBody = False
            inRequest = False
            continue
        elif(re.search(r"\+ Header", setence) != None):
            inHeader = True
            inBody = False
        elif(re.search(r"\+ Attribute", setence) != None):
            if(re.search(r"\(array", setence) != None):
                apiList[-1].isBodyArray = True
            inBody = True
            inHeader = False
            matchObj = re.search(r"[\(array\[|\(]([A-Z]\w+)", setence)
            if(matchObj != None):
                apiList[-1].body = {"waitObject": matchObj.group(1)}
                inBody = False
        if(inHeader):
            header = getRequestHeader(setence)
            if(header != None):
                apiList[-1].header.append(header)
        if(inBody):
            body = getRequestBody(setence)
            if(body != None and re.search(r"optional\)", setence) == None):
                bodyObj = re.search(r"\+ .*[\(|\(array\[]([A-Z]\w+)", setence)
                apiList[-1].body[body] = ""
                if(bodyObj != None):
                    apiList[-1].body[body] = {"waitObject": bodyObj.group(1)}

def findDataStruct(key):
    for name in list(dataStrucList):
        if(name == key):
            return name
    return "error_body"

## Handle the situation that document write datastructure in API's document
# def isDefalutValue(value):
#     if(value == False or value == 0 or value == "" or len(value) == 0):
#         return True
#     return False

# index = 0
# for (name, struct) in dataStrucList:
#     for key in struct:
#         if(isDefalutValue(struct[key]) is False):
#             structIndex = findDataStruct(struct[key])
#             if(type(structIndex) == int):
#                 (_, inStruct) = dataStrucList[structIndex]
#                 struct[key] = inStruct
#                 dataStrucList[index] = (name, struct)
#     index += 1

index = 0
for i in apiList:
    if(i.method != ""):
        if("waitObject" in i.body):
            structKey = findDataStruct(apiList[index].body["waitObject"])
            req_body = dataStrucList[structKey]
            apiList[index].body = req_body
    index += 1

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

def addApi(name, url, method, parameter, header, body):
    txt["item"].append({
        "name": name,
        "request": {
            "method": method,
            "header": genHeaders(header, body),
            "body": genBody(body),
            "url": genUrl(url)
        }
    })

for i in apiList:
    if(i.method != ""):
        addApi(i.name, i.path, i.method, i.parameter, i.header, i.body)
# print(txt)

with open(file_name +".json", "w") as fp:
    json.dump(txt, fp, indent=2, ensure_ascii=False)
