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
# 由于是拼接的，因此把大文档的id乘以10000，加上文档内序号的id
def getDocID(filename):
    end = filename.find('.')
    docId = filename[0:end]
    docID = docId.split('-')

    return int(docID[0])*10000+int(docID[1])

# 展示id，形式为xxx-xx
def showDocID(id):
    return str(id//10000) + '-' + str(id%10000)

# 主id，形式为xxx
def mainDocID(id):
    return id//10000

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