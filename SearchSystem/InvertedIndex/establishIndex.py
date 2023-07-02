import copy
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
    
    # assign path
    path = tools.projectpath + directname
    path = tools.reuterspath
    files = os.listdir(path)
    files=[file for file in files if file.find('.')!=-1]  # skip folder

    invertedIndex = {}  # 完整的index
    invertedIndex_qa = {} # qa的index
    invertedIndex_qq = {} # qq的index
    wordCount={}  # 完整的wordcount
    wordCount_qa={}  # qa的wordcount
    wordCount_qq={}  # qq的wordcount
    #单词:docid:[pos]
    for file in files:
        print("analyzing file: ", file)

        contents = PreprocessFile.preProcess_zh_qa(path + '/' + file)
        titles = PreprocessFile.preProcess_zh_qq(path + '/' + file)
        # skip empty files
        if len(contents)==0:
            continue

        # 处理qa
        # docId = tools.getDocID(file)#文档name必须是 xxx-xx
        docId_qa=tools.getDocID_qa(file)
        wordCount_qa[docId_qa]=len(contents)
        num = 0 #word在文档中的位置

        for word in contents:
            # 处理qa的index
            if word not in invertedIndex_qa:
                docList = {}
                docList[docId_qa] = [num]
                invertedIndex_qa[word] = copy.deepcopy(docList)
            else:
                if docId_qa not in invertedIndex_qa[word]:
                    invertedIndex_qa[word][docId_qa] = [num]
                else:
                    invertedIndex_qa[word][docId_qa].append(num)

            num += 1
        
        # 处理qq
        docId_qq=tools.getDocID_qq(file)
        wordCount_qq[docId_qq]=len(titles)
        num = 0 #word在文档中的位置

        for word in titles:
            # 处理qq的index
            if word not in invertedIndex_qq:
                docList = {}
                docList[docId_qq] = [num]
                invertedIndex_qq[word] = (docList)
            else:
                if docId_qq not in invertedIndex_qq[word]:
                    invertedIndex_qq[word][docId_qq] = [num]
                else:
                    invertedIndex_qq[word][docId_qq].append(num)

            num += 1
        
    # 合并qq和qa的index和wordCount为完整的版本
    for word in invertedIndex_qa:
        if word not in invertedIndex:
            invertedIndex[word]=copy.deepcopy(invertedIndex_qa[word])
        else:
            invertedIndex[word].update(invertedIndex_qa[word])
    
    for word in invertedIndex_qq:
        if word not in invertedIndex:
            invertedIndex[word]=copy.deepcopy(invertedIndex_qq[word])
        else:
            invertedIndex[word].update(invertedIndex_qq[word])
    
    wordCount.update(wordCount_qa)
    wordCount.update(wordCount_qq)

    #处理qa的index和wordCount
    #给倒排索引中的词项排序
    invertedIndex_qa = sortTheDict(invertedIndex_qa)
    #获取词项列表
    wordList_qa = getWordList(invertedIndex_qa)
    printIndex(invertedIndex_qa)
    #将数据写入文件中
    tools.writeToFile_zh(invertedIndex_qa, tools.projectpath + 'invertIndex_zh_qa.json')
    tools.writeToFile_zh(wordList_qa, tools.projectpath + 'wordList_zh_qa.json')
    tools.writeToFile_zh(wordCount_qa, tools.projectpath + 'wordCount_zh_qa.json')

    #处理qq的index和wordCount
    #给倒排索引中的词项排序
    invertedIndex_qq = sortTheDict(invertedIndex_qq)
    #获取词项列表
    wordList_qq = getWordList(invertedIndex_qq)
    printIndex(invertedIndex_qq)
    #将数据写入文件中
    tools.writeToFile_zh(invertedIndex_qq, tools.projectpath + 'invertIndex_zh_qq.json')
    tools.writeToFile_zh(wordList_qq, tools.projectpath + 'wordList_zh_qq.json')
    tools.writeToFile_zh(wordCount_qq, tools.projectpath + 'wordCount_zh_qq.json')


    # 处理完整的index和wordCount
    #给倒排索引中的词项排序
    invertedIndex = sortTheDict(invertedIndex)
    #获取词项列表
    wordList = getWordList(invertedIndex)
    printIndex(invertedIndex)
    #将数据写入文件中
    tools.writeToFile_zh(invertedIndex, tools.projectpath + 'invertIndex_zh.json')
    tools.writeToFile_zh(wordList, tools.projectpath + 'wordList_zh.json')
    tools.writeToFile_zh(wordCount, tools.projectpath + 'wordCount_zh.json')

    # set establishIndex in config to false
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
