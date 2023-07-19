import hashlib
import json
import os
import time
import yaml

projectpath = os.path.abspath(__file__)
projectpath = projectpath[:projectpath.find('jingemen_planb') + len('jingemen_planb')]
print(f'projectpath is {projectpath}')
searchsystempath = os.path.join(projectpath,"SearchSystem")
# searchsystempath = searchsystempath.replace('/',"\\")
while(not searchsystempath.endswith("SearchSystem")):
    print(searchsystempath)
    searchsystempath = os.path.dirname(searchsystempath)
indexpath = os.path.join(searchsystempath,'index/')
reuterspath = os.path.join(searchsystempath,"pairs/")
config={}
secret={}
print("searchsystempath:",searchsystempath)
print("indexpath:",indexpath)
print("Reuters path",reuterspath)
renew_path=[reuterspath+x for x in os.listdir(reuterspath) if x.endswith(".json")]
# sort renew_path by alphabet
renew_path.sort()

def writeToFile(item,filename):
    # 将数据写入到文件中
    file = open(filename,'w')
    str = json.JSONEncoder().encode(item)
    file.write(str)
    file.close()

def writeToFile_zh(item,filename,method='index'):
    # 将数据写入到文件中
    if method=='index':
        file = open(indexpath+filename,'w',encoding='utf-8')
        str = json.dumps(item, ensure_ascii=False)
        file.write(str)
        file.close()

def readFile_zh(filename,method='index'):
    # 读取文件中的数据
    if method=='index':
        file = open(indexpath+filename,'r',encoding='utf-8')
        str = file.read()
        item = json.JSONDecoder().decode(str)
        file.close()
    return item

def listFile_zh(subpath='',method='index'):
    # 列出文件夹中的文件
    if method=='index':
        files = os.listdir(indexpath+subpath)
    return files

#获取文档名中的文档的id
# 由于是拼接的，因此把大文档的id乘以10000，加上文档内序号的id
def getDocID(filename):
    docId = filename.split('.')[0]
    docID = docId.split('-')

    return int(docID[0])*10000+int(docID[1])

def getDocID_qq(filename):
    docId = filename.split('.')[0]
    docID = docId.split('-')

    return int(docID[0])*10000+int(docID[1])+1000

def getDocID_qa(filename):
    docId = filename.split('.')[0]
    docID = docId.split('-')

    return int(docID[0])*10000+int(docID[1])

# 展示id，形式为xxx-xx
def showDocID(id):
    return str(id//10000) + '-' + str(id%100)

# 主id，形式为xxx
def mainDocID(id):
    # if id is a int
    if isinstance(id,int):
        return id//10000
    # if id is a str
    elif isinstance(id,str):
        return int(id.split('-')[0])

        

def getWholeDocList():
    files = os.listdir(reuterspath)
    fileList = []
    for file in files:
        # skip fold
        if file.find('.') == -1:
            continue
        fileList.append(getDocID(file))
    return sorted(fileList)

def getRetrieveMethod(id):
    method= id%10000
    method//=1000

    if method==0:
        return 'qq'
    elif method==1:
        return 'qa'
    else:
        return 'qa + qq'

def setRetrieveMethod(id,method):
    if method == 'qa':
        id = id//10000*10000 + 1000 + id%1000
    elif method == 'qq':
        id = id//10000*10000 + id%1000
    else:
        id = id//10000*10000 + 2000 + id%1000
    return id

def initConfig():
    global config
    global secret
    with open(os.path.join(searchsystempath ,'SearchConfig.yaml'),'r',encoding="utf-8") as f:
        config = yaml.safe_load(f)
    with open(os.path.join(searchsystempath, 'secret.yaml'),'r',encoding="utf-8") as f:
        secret = yaml.safe_load(f)
        # set"OPENAI_API_KEY" in secret as environment variable
        os.environ["OPENAI_API_KEY"]=secret["OPENAI_API_KEY"]
        print(os.getenv("OPENAI_API_KEY"))
    # 看看是否需要建立索引
    check_renew_index()


def getConfig(str):
    global config
    return config[str]

def setConfig(str,value):
    global config
    print(f'setting {str} as {value}')
    config[str] = value
    with open(searchsystempath + 'SearchConfig.yaml','w') as f:
        yaml.dump(config,f)

def searchSystemPath(file):
    return os.path.join(searchsystempath,file)

def check_renew_index():
    global renew_path
    start_time = time.time()
    hasher = hashlib.new('sha256')
    for file_path in renew_path:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                hasher.update(data)
        end_time = time.time()
        print(f"计算 {file_path} 的哈希值用时：{end_time - start_time} 秒。")
    if hasher.hexdigest() == getConfig("index_hash"):
        return
    setConfig("index_hash",hasher.hexdigest())
    setConfig("establishIndex",True)
    setConfig("new_embedding",True)

print("getting file list...")
# wholeDocList = getWholeDocList()
initConfig()

