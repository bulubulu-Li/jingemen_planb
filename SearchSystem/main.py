import os
import tools
import nltk
from InvertedIndex import getIndex
from LanguageAnalysis import stemming
from Serching import searchWord
from SpellingCorrect import spell
from scoreQuery import sortDoc
from BoolSearch import BoolSearchDel
from InvertedIndex import establishIndex
from LargeLanguageModel import chain
import jieba
#下载需要的依赖文件
# nltk.download("wordnet")
# nltk.download("averaged_perceptron_tagger")
# nltk.download("punkt")
# nltk.download("maxent_treebank_pos_tagger")

DIRECTNAME = 'Reuters_zh'

#建立索引
establishIndex.createIndex_zh()

print("getting word list...")
WORDLIST = getIndex.getWordList_zh()

print("getting index...")
INDEX = getIndex.getIndex_zh()
INDEX_QQ = getIndex.getIndex_zh_qq()
INDEX_QA = getIndex.getIndex_zh_qa()

print("loading the wordnet...")
WORDCOUNT = getIndex.getWordCount_zh()
WORDCOUNT_QQ = getIndex.getWordCount_zh_qq()
WORDCOUNT_QA = getIndex.getWordCount_zh_qa()
# stemming.lemmatize_sentence("a", False)
 
PATH = tools.reuterspath
FILES = os.listdir(tools.reuterspath)
FILENUM = len(FILES)-3

LOOP = True
print("=================Searching System=================")

# 词形还原+纠错
def preCheck(statement):
    return statement
    print("spelling correcting...")
    INPUTWORDS = spell.correctSentence(INPUTWORDS)
    print(INPUTWORDS)
    print("stemming...")
    INPUTWORDS = stemming.lemmatize_sentence(statement, True)
    print(INPUTWORDS)
    return INPUTWORDS

def preCheck_zh(statement):
    # print("分词...")
    INPUTWORDS = jieba.cut(statement)
    return INPUTWORDS

def check_expect(doclist,expectlist):
    # print("check_expect...")
    res=[]
    docs=[x[1] for x in doclist]
    for i,doc in enumerate(docs):
        if doc in expectlist:
            res.append(doclist[i])
            res[-1].append(i)
    return res

def searching(statement,choice,loop=False,expectList=[] ):
    # 查询排序
    # print("searching...")
    STATEMENT = statement
    source=[]
    # 倒排全部查找
    if choice == 1: 
        INPUTWORDS=preCheck_zh(STATEMENT)

        WORDSET = set(INPUTWORDS)

        DOCLIST = searchWord.searchWords(INDEX, WORDSET)
        SORTEDDOCLIST = sortDoc.TopKScore(40, INDEX, FILENUM, WORDSET, DOCLIST,WORDCOUNT)
        # print(SORTEDDOCLIST)
        source=check_expect(SORTEDDOCLIST,expectList)
        if loop==False:
            return SORTEDDOCLIST, source
        for doc in SORTEDDOCLIST:
            print("doc ID: ",tools.showDocID(doc[1]), " score: ", "%.3f" % doc[0])
        
    # 倒排qq查找
    if choice == 2: 
        INPUTWORDS=preCheck_zh(STATEMENT)

        WORDSET = set(INPUTWORDS)

        DOCLIST = searchWord.searchWords(INDEX_QQ, WORDSET)
        SORTEDDOCLIST = sortDoc.TopKScore(40, INDEX_QQ, FILENUM, WORDSET, DOCLIST,WORDCOUNT_QQ)
        source=check_expect(SORTEDDOCLIST,expectList)
        if loop==False:
            return SORTEDDOCLIST, source
        for doc in SORTEDDOCLIST:
            print("doc ID: ",tools.showDocID(doc[1]), " score: ", "%.3f" % doc[0])
        
    # 倒排qa查找
    if choice == 3: 
        INPUTWORDS=preCheck_zh(STATEMENT)

        WORDSET = set(INPUTWORDS)

        DOCLIST = searchWord.searchWords(INDEX_QA, WORDSET)
        SORTEDDOCLIST = sortDoc.TopKScore(40, INDEX_QA, FILENUM, WORDSET, DOCLIST,WORDCOUNT_QA)
        source=check_expect(SORTEDDOCLIST,expectList)
        if loop==False:
            return SORTEDDOCLIST, source
        for doc in SORTEDDOCLIST:
            print("doc ID: ",tools.showDocID(doc[1]), " score: ", "%.3f" % doc[0])

    # qq qa 各召回一部分
    if choice == 4:
        INPUTWORDS=preCheck_zh(STATEMENT)

        WORDSET = set(INPUTWORDS)

        DOCLIST_QQ = searchWord.searchWords(INDEX_QQ, WORDSET)
        SORTEDDOCLIST_QQ = sortDoc.TopKScore(20, INDEX_QQ, FILENUM, WORDSET, DOCLIST_QQ,WORDCOUNT_QQ)

        DOCLIST_QA = searchWord.searchWords(INDEX_QA, WORDSET)
        SORTEDDOCLIST_QA = sortDoc.TopKScore(20, INDEX_QA, FILENUM, WORDSET, DOCLIST_QA,WORDCOUNT_QA)

        SORTEDDOCLIST = SORTEDDOCLIST_QQ + SORTEDDOCLIST_QA
        SORTEDDOCLIST=sorted(SORTEDDOCLIST,key=lambda x:x[0],reverse=True)

        source=check_expect(SORTEDDOCLIST,expectList)
        if loop==False:
            return SORTEDDOCLIST, source



    # #TOP K 查询
    # elif choice == 2:
    #     INPUTWORDS=preCheck_zh(STATEMENT)

    #     WORDSET = set(INPUTWORDS)

    #     DOCLIST = searchWord.searchWords(INDEX, WORDSET)
    #     # print(DOCLIST)
    #     #根据tf-idf计算分数
    #     #取top20
    #     SORTEDDOCLIST = sortDoc.TopKScore(20, INDEX, FILENUM, WORDSET, DOCLIST,WORDCOUNT)
    #     for doc in SORTEDDOCLIST:
    #         print("doc ID: ", tools.showDocID(doc[1]), " score: ", "%.3f" % doc[0])
    #     if loop==False:
    #         return SORTEDDOCLIST
    # #Bool 查询
    # elif choice == 3:
    #     INPUTWORDS=preCheck_zh(STATEMENT)

    #     DOCLIST = BoolSearchDel.BoolSearch(INPUTWORDS, INDEX)
    #     print(len(DOCLIST),"DOCs :")
    #     print(DOCLIST)
    # #短语查询
    # elif choice == 4:
    #     INPUTWORDS=preCheck_zh(STATEMENT)

    #     WORDSET = set(INPUTWORDS)

    #     PHRASEDOCLIST = searchWord.searchPhrase(INDEX, WORDSET, INPUTWORDS)
    #     if 0 == len(PHRASEDOCLIST):
    #         print("Doesn't find \"", INPUTWORDS, '"')
    #     else:
    #         for key in PHRASEDOCLIST:
    #             print('docID: ', key, "   num: ", len(PHRASEDOCLIST[key]))
    #             print('    location: ', PHRASEDOCLIST[key])
    #模糊查询
    elif choice == 5:
        list = searchWord.wildcardSearch(STATEMENT, INDEX, WORDLIST)

    elif choice == 6:
        INPUTWORDS=preCheck_zh(STATEMENT)

        WORDSET = set(INPUTWORDS)

        resultlist = searchWord.searchSynonymsWord(INDEX,INPUTWORDS[0])

    elif choice == 7:
        retrieve_res=chain.Retrieve(STATEMENT,PATH)
        res=[x["matedata"]["docID"] for x in retrieve_res]
        if loop==False:
            return res,[]
        print(chain.Retrieve(STATEMENT,PATH))


if __name__ == '__main__':
    while LOOP:
        print("searching operation: ")
        print("[1]qa mix qq [2]qq [3]qa [4]qa + qq [5]wildcard [6]synonyms [7]LLM [88]exit")
        print("your choice(int):")
        try:
            choice = int(input())
            if choice == 88:
                break
        except :
            print()
            continue

        if choice >= 1 and choice <= 7:
            print("input the query statement:")
            STATEMENT = input()
            if STATEMENT == "EXIT":
                break

            #查询排序
            searching(STATEMENT,choice,True)


        else:
            print("Invalid choice! Please observe these choices carefully!")
        print()

    print("ByeBye!")


# establishVSM.createVSM(INDEX,WORDLIST,'test')
