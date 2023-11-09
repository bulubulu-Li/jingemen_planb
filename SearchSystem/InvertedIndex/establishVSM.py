import cmath
import os
import SearchSystem.tools as tools
from Log.log import log

def createVSM(index, wordList, directname):
    path = tools.searchsystempath + directname
    files = os.listdir(path)
    fileNum = len(files)
    VSM = {}
    for file in files:
        fileID = str(getDocID(file))
        tf_idf_list = []
        for word in wordList:
            if fileID not in index[word] :
                tf_idf_list.append(0)
                continue

            tf = len(index[word][str(fileID)])

            df = len(index[word])
            #保留三位小数
            idf = cmath.log10(fileNum / df).real
            # idf =  float("%.3f" % cmath.log(10 , fileNum / df).real)
            tf_idf = "%.2f" % float(tf * idf)

            tf_idf_list.append(tf_idf)

        VSM[fileID] = tf_idf_list
        # log.info(tf_idf_list)
    tools.writeToFile(VSM, tools.searchsystempath + 'VSM.json')
    #return VSM



# 获取文档名中的文档的id
def getDocID(filename):
    end = filename.find('.')
    docId = filename[0:end]
    return int(docId)
