import os
import sys
import time

try:
    from Log.log import log
except:
    projectpath = os.path.abspath(__file__)
    projectpath = projectpath[:projectpath.find('jingemen_planb') + len('jingemen_planb')]
    print(f'projectpath is {projectpath}')
    if sys.path.count(projectpath)==0:
        sys.path.append(projectpath)
    from Log.log import log


import SearchSystem.tools as tools
import nltk
from SearchSystem.InvertedIndex import getIndex
from SearchSystem.LanguageAnalysis import stemming
from SearchSystem.Serching import searchWord
# from SearchSystem.SpellingCorrect import spell
from SearchSystem.scoreQuery import sortDoc
from SearchSystem.BoolSearch import BoolSearchDel
from SearchSystem.InvertedIndex import establishIndex
from SearchSystem.LargeLanguageModel import chain
from SearchSystem.DataManager import BaseDataManager, DataForm
import jieba
import re
from rouge import Rouge

# 下载需要的依赖文件
# nltk.download("wordnet")
# nltk.download("averaged_perceptron_tagger")
# nltk.download("punkt")
# nltk.download("maxent_treebank_pos_tagger")

DIRECTNAME = 'Reuters_zh'

# 建立索引
establishIndex.createIndex_zh()
manager = BaseDataManager()
log.info("getting word list...")
WORDLIST = getIndex.getWordList_zh()

log.info("getting index...")
INDEX = getIndex.getIndex_zh()
INDEX_QQ = getIndex.getIndex_zh_qq()
INDEX_QA = getIndex.getIndex_zh_qa()

log.info("loading the wordnet...")
WORDCOUNT = getIndex.getWordCount_zh()
WORDCOUNT_QQ = getIndex.getWordCount_zh_qq()
WORDCOUNT_QA = getIndex.getWordCount_zh_qa()
# stemming.lemmatize_sentence("a", False)

PATH = tools.reuterspath
FILES = os.listdir(tools.reuterspath)
FILENUM = manager.len

LOOP = True
log.info("=================Searching System=================")

# 词形还原+纠错


def preCheck(statement):
    return statement
    log.info("spelling correcting...")
    INPUTWORDS = spell.correctSentence(INPUTWORDS)
    log.info(INPUTWORDS)
    log.info("stemming...")
    INPUTWORDS = stemming.lemmatize_sentence(statement, True)
    log.info(INPUTWORDS)
    return INPUTWORDS


def preCheck_zh(statement):
    # log.info("分词...")
    INPUTWORDS = jieba.cut(statement)
    return INPUTWORDS


def check_expect(doclist, expectlist):
    # log.info("check_expect...")
    res = []
    docs = [x[1] for x in doclist]
    for i, doc in enumerate(docs):
        if doc in expectlist:
            res.append(doclist[i])
            res[-1].append(i)
    return res


def searchResults(statement, choice=1, loop=False, expectList=[]):
    """
    
    当不是embeding模式的时候返回一个返回值，这个返回值是一个文档列表
    当是embedding模式的时候，返回三个返回值，分别为生成的结果，参考文献列表和对应的片段。

    """
    searchRes, _ = searching(statement, choice, loop, expectList)
    docList = []
    if choice != 7:
        for x in searchRes:
            if manager.get_docId(x[1]) not in docList:
                docList.append(manager.get_docId(x[1]))
        if len(docList) > 3:
            docList = docList[:3]

        res = [manager[x] for x in docList]
        return res
    
    else:

        result,docList=searching(statement, choice)

        return result,[manager[int(x.metadata["docId"])] for x in docList],[x.page_content for x in docList]







def searching(statement, choice=1, loop=False, expectList=[]):
    """
    
    """
    # 查询排序
    # log.info("searching...")
    STATEMENT = statement
    source = []
    # 倒排全部查找
    if choice == 1:
        INPUTWORDS = preCheck_zh(STATEMENT)

        WORDSET = set(INPUTWORDS)

        DOCLIST = searchWord.searchWords(INDEX, WORDSET)
        SORTEDDOCLIST = sortDoc.TopKScore(40, INDEX, FILENUM, WORDSET, DOCLIST, WORDCOUNT)
        # log.info(SORTEDDOCLIST)
        source = check_expect(SORTEDDOCLIST, expectList)
        log.info(SORTEDDOCLIST)
        if loop == False:
            return SORTEDDOCLIST, source
        for doc in SORTEDDOCLIST:
            log.info(f"doc ID: {tools.showDocID(doc[1])} score: {doc[0]:.3f}" )

    # 倒排qq查找
    if choice == 2:
        INPUTWORDS = preCheck_zh(STATEMENT)

        WORDSET = set(INPUTWORDS)

        DOCLIST = searchWord.searchWords(INDEX_QQ, WORDSET)
        SORTEDDOCLIST = sortDoc.TopKScore(40, INDEX_QQ, FILENUM, WORDSET, DOCLIST, WORDCOUNT_QQ)
        source = check_expect(SORTEDDOCLIST, expectList)
        if loop == False:
            return SORTEDDOCLIST, source
        for doc in SORTEDDOCLIST:
            log.info(f"doc ID: {tools.showDocID(doc[1])} score: {doc[0]:.3f}" )

    # 倒排qa查找
    if choice == 3:
        INPUTWORDS = preCheck_zh(STATEMENT)

        WORDSET = set(INPUTWORDS)

        DOCLIST = searchWord.searchWords(INDEX_QA, WORDSET)
        SORTEDDOCLIST = sortDoc.TopKScore(40, INDEX_QA, FILENUM, WORDSET, DOCLIST, WORDCOUNT_QA)
        source = check_expect(SORTEDDOCLIST, expectList)
        if loop == False:
            return SORTEDDOCLIST, source
        for doc in SORTEDDOCLIST:
            log.info(f"doc ID: {tools.showDocID(doc[1])} score: {doc[0]:.3f}" )

    # qq qa 各召回一部分
    if choice == 4:
        INPUTWORDS = preCheck_zh(STATEMENT)

        WORDSET = set(INPUTWORDS)

        DOCLIST_QQ = searchWord.searchWords(INDEX_QQ, WORDSET)
        SORTEDDOCLIST_QQ = sortDoc.TopKScore(20, INDEX_QQ, FILENUM, WORDSET, DOCLIST_QQ, WORDCOUNT_QQ)

        DOCLIST_QA = searchWord.searchWords(INDEX_QA, WORDSET)
        SORTEDDOCLIST_QA = sortDoc.TopKScore(20, INDEX_QA, FILENUM, WORDSET, DOCLIST_QA, WORDCOUNT_QA)

        SORTEDDOCLIST = SORTEDDOCLIST_QQ + SORTEDDOCLIST_QA
        SORTEDDOCLIST = sorted(SORTEDDOCLIST, key=lambda x: x[0], reverse=True)

        source = check_expect(SORTEDDOCLIST, expectList)
        if loop == False:
            return SORTEDDOCLIST, source

    # #TOP K 查询
    # elif choice == 2:
    #     INPUTWORDS=preCheck_zh(STATEMENT)

    #     WORDSET = set(INPUTWORDS)

    #     DOCLIST = searchWord.searchWords(INDEX, WORDSET)
    #     # log.info(DOCLIST)
    #     #根据tf-idf计算分数
    #     #取top20
    #     SORTEDDOCLIST = sortDoc.TopKScore(20, INDEX, FILENUM, WORDSET, DOCLIST,WORDCOUNT)
    #     for doc in SORTEDDOCLIST:
    #         log.info("doc ID: ", tools.showDocID(doc[1]), " score: ", "%.3f" % doc[0])
    #     if loop==False:
    #         return SORTEDDOCLIST
    # #Bool 查询
    # elif choice == 3:
    #     INPUTWORDS=preCheck_zh(STATEMENT)

    #     DOCLIST = BoolSearchDel.BoolSearch(INPUTWORDS, INDEX)
    #     log.info(len(DOCLIST),"DOCs :")
    #     log.info(DOCLIST)
    # #短语查询
    # elif choice == 4:
    #     INPUTWORDS=preCheck_zh(STATEMENT)

    #     WORDSET = set(INPUTWORDS)

    #     PHRASEDOCLIST = searchWord.searchPhrase(INDEX, WORDSET, INPUTWORDS)
    #     if 0 == len(PHRASEDOCLIST):
    #         log.info("Doesn't find \"", INPUTWORDS, '"')
    #     else:
    #         for key in PHRASEDOCLIST:
    #             log.info('docID: ', key, "   num: ", len(PHRASEDOCLIST[key]))
    #             log.info('    location: ', PHRASEDOCLIST[key])
    # 模糊查询
    # elif choice == 5:
    #     list = searchWord.wildcardSearch(STATEMENT, INDEX, WORDLIST)

    # elif choice == 6:
    #     INPUTWORDS = preCheck_zh(STATEMENT)

    #     WORDSET = set(INPUTWORDS)

    #     resultlist = searchWord.searchSynonymsWord(INDEX, INPUTWORDS[0])

    elif choice == 7:
        retrieve_res = chain.Retrieve(STATEMENT)
        log.info(retrieve_res)
        answer=retrieve_res["result"]
        # 找出answer中的参考文献，使用的方式是找出所有被[]包裹的数字，然后保留unique的
        # 参考文献的格式是[1] [2] [3]，所以可以用正则表达式匹配
        # referenceList=[]
        # for x in re.findall(r"\[\d+\]",answer):
        #     if x not in referenceList:
        #         referenceList.append({
        #             "index":x,
        #             "doc":
        #         })
        # log.info(referenceList)
        rouge = Rouge()
        source = []
        # 如果result包含“未找到答案”，直接返回
        if "未找到答案" in retrieve_res["result"]:
            return answer,[]
        a = retrieve_res["result"].split('。')
        if '' in a:
            a.remove('')
        for sub_string in a:
            tmp_score = []
            for i in range(len(retrieve_res["source_documents"])):
                sub_doc = retrieve_res["source_documents"][i]
                rouge_score = rouge.get_scores([' '.join(list(sub_string))], [' '.join(list(sub_doc.page_content))])
                tmp_score.append(rouge_score[0]["rouge-l"]['f'])
            log.info(f"tmp_score: {tmp_score}")

            source.append(tmp_score.index(max(tmp_score)))

        log.info(f"source: {source}" )
        temp=[]
        for x in source:
            if x not in temp:
                temp.append(x)
        
        docList = [retrieve_res["source_documents"][x] for x in temp]
        
        log.info(f"answer {answer}, docList {docList}")

        if loop == False:
            return answer,docList
        # log.info(chain.Retrieve(STATEMENT, PATH))


# if __name__ == '__main__':
#     while LOOP:
#         log.info("searching operation: ")
#         log.info(
#             "[1]qa mix qq [2]qq [3]qa [4]qa + qq [5]wildcard [6]synonyms [7]LLM [88]exit")
#         log.info("your choice(int):")
#         try:
#             choice = int(input())
#             if choice == 88:
#                 break
#         except:
#             log.info()
#             continue

#         if choice >= 1 and choice <= 7:
#             log.info("input the query statement:")
#             STATEMENT = input()
#             if STATEMENT == "EXIT":
#                 break

#             # 查询排序
#             searching(STATEMENT, choice, True)

#         else:
#             log.info("Invalid choice! Please observe these choices carefully!")
#         log.info()

#     log.info("ByeBye!")

start_time = time.time()
for i in range(10):
    retrieve_res = searching("老年人优待证怎么办理",choice=7)
end_time = time.time()
print("Time taken to process the sentence: ", end_time - start_time, "seconds")
# log.info(retrieve_res)
# establishVSM.createVSM(INDEX,WORDLIST,'test')
