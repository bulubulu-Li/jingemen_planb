import json
import os

projectpath = os.getcwd()
projectpath = projectpath.replace('/',"\\")
projectpath += "\\"
reuterspath = projectpath.replace("SearchSystem","Reuters_zh")
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

print("getting file list...")
wholeDocList = getWholeDocList()