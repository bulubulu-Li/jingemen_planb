import os
import tools
from LanguageAnalysis import PreprocessFile
import jieba

def createIndex(directname):
    invertedIndex = {}
    path = tools.projectpath + directname
    path = tools.reuterspath
    files = os.listdir(path)

    #单词:docid:[pos]
    for file in files:
        print("analyzing file: ", file)
        #每个文档的词项 list
        #此处，需要做一个分词，还需要设置停用词，做过滤
        #然后，保存jingmen数据为html
        #然后就没啥大问题了
        content = PreprocessFile.preProcess(path + '/' + file)
        docId = tools.getDocID(file)#文档name必须是数字

        num = 0 #word在文档中的位置
        for word in content:
            # if word.isdigit():
            #     num += 1
            #     continue

            if word not in invertedIndex:
                docList = {}
                docList[docId] = [num]
                invertedIndex[word] = docList
            else:
                if docId not in invertedIndex[word]:
                    invertedIndex[word][docId] = [num]
                else:
                    invertedIndex[word][docId].append(num)

            num += 1

    #给倒排索引中的词项排序
    invertedIndex = sortTheDict(invertedIndex)
    #获取词项列表
    wordList = getWordList(invertedIndex)

    printIndex(invertedIndex)

    #将数据写入文件中
    tools.writeToFile(invertedIndex, tools.projectpath + 'invertIndex.json')
    tools.writeToFile(wordList, tools.projectpath + 'wordList.json')

def createIndex_zh(directname):
    # if establishindex in config is false, read from exist file, else generate
    if tools.getConfig("establishIndex") == False:
        return
    
    invertedIndex = {}
    path = tools.projectpath + directname
    path = tools.reuterspath
    files = os.listdir(path)
    wordCount={}

    #单词:docid:[pos]
    for file in files:
        print("analyzing file: ", file)
        #每个文档的词项 list
        #此处，需要做一个分词，还需要设置停用词，做过滤
        #然后，保存jingmen数据为html
        #然后就没啥大问题了
        # skip fold
        if file.find('.') == -1:
            continue
        content = PreprocessFile.preProcess_zh(path + '/' + file)
        # skip empty files
        if len(content)==0:
            continue

        docId = tools.getDocID(file)#文档name必须是 xxx-xx
        wordCount[docId]=len(content)
        
        num = 0 #word在文档中的位置
        for word in content:
            # if word.isdigit():
            #     num += 1
            #     continue

            if word not in invertedIndex:
                docList = {}
                docList[docId] = [num]
                invertedIndex[word] = docList
            else:
                if docId not in invertedIndex[word]:
                    invertedIndex[word][docId] = [num]
                else:
                    invertedIndex[word][docId].append(num)

            num += 1

    #给倒排索引中的词项排序
    invertedIndex = sortTheDict(invertedIndex)
    #获取词项列表
    wordList = getWordList(invertedIndex)

    printIndex(invertedIndex)

    #将数据写入文件中
    tools.writeToFile_zh(invertedIndex, tools.projectpath + 'invertIndex_zh.json')
    tools.writeToFile_zh(wordList, tools.projectpath + 'wordList_zh.json')
    tools.writeToFile_zh(wordCount, tools.projectpath + 'wordCount_zh.json')
    tools.setConfig("establishIndex", False)






def sortTheDict(dict):
    sdict =  { k:dict[k] for k in sorted(dict.keys())}
    for stem in sdict:
        sdict[stem] = { k:sdict[stem][k] for k in sorted(sdict[stem].keys())}
    return sdict

def printIndex(index):
    for stem in index:
        print(stem)
        for doc in index[stem]:
            print("    " , doc , " : " , index[stem][doc])

def getWordList(invertedIndex):
    wordList = []
    for word in invertedIndex.keys():
        wordList.append(word)
    return wordList

# print("establishing the INDEX...")
# establishIndex.createIndex('Reuters')



# createIndex('test')
