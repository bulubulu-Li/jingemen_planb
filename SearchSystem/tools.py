import json
import os

import yaml

projectpath = os.getcwd()
projectpath = projectpath.replace('/',"\\")
projectpath += "\\"
reuterspath = projectpath.replace("SearchSystem","Reuters_zh")
config={}
secret={}
print("projectpath:",projectpath)
print("Reuters path",reuterspath)

def writeToFile(item,filename):
    # 将数据写入到文件中
    file = open(filename,'w')
    str = json.JSONEncoder().encode(item)
    file.write(str)
    file.close()

def writeToFile_zh(item,filename):
    # 将数据写入到文件中
    file = open(filename,'w',encoding='utf-8')
    str = json.JSONEncoder().encode(item)
    file.write(str)
    file.close()

#获取文档名中的文档的id
def getDocID(filename):
    end = filename.find('.')
    docId = filename[0:end]
    return int(docId)

def getWholeDocList():
    files = os.listdir(reuterspath)
    fileList = []
    for file in files:
        # skip fold
        if file.find('.') == -1:
            continue
        fileList.append(getDocID(file))
    return sorted(fileList)

def initConfig():
    global config
    global secret
    with open(projectpath + 'SearchConfig.yaml','r',encoding="utf-8") as f:
        config = yaml.safe_load(f)
    with open(projectpath + 'secret.yaml','r',encoding="utf-8") as f:
        secret = yaml.safe_load(f)
        # set"OPENAI_API_KEY" in secret as environment variable
        os.environ["OPENAI_API_KEY"]=secret["OPENAI_API_KEY"]
        print(os.getenv("OPENAI_API_KEY"))


def getConfig(str):
    global config
    return config[str]

def setConfig(str,value):
    global config
    config[str] = value
    with open(projectpath + 'SearchConfig.yaml','w') as f:
        yaml.dump(config,f)

print("getting file list...")
wholeDocList = getWholeDocList()
initConfig()