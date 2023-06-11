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
establishIndex.createIndex_zh(DIRECTNAME)

print("getting word list...")
WORDLIST = getIndex.getWordList_zh()
print("getting index...")
INDEX = getIndex.getIndex_zh()
print("loading the wordnet...")
# stemming.lemmatize_sentence("a", False)
 
PATH = tools.reuterspath
FILES = os.listdir(tools.reuterspath)
FILENUM = len(FILES)

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
    print("分词...")
    INPUTWORDS = jieba.cut(statement)
    return INPUTWORDS

while LOOP:
    print("searching operation: ")
    print("[1] Overall [2]TOP K [3]BOOL [4]Phrase [5]wildcard [6]synonyms [7]LLM [8]exit")
    print("your choice(int):")
    try:
        choice = int(input())
        if choice == 8:
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
        if choice == 1:
            INPUTWORDS=preCheck_zh(STATEMENT)

            WORDSET = set(INPUTWORDS)

            DOCLIST = searchWord.searchWords(INDEX, WORDSET)
            SORTEDDOCLIST = sortDoc.sortScoreDocList(INDEX, FILENUM, WORDSET, DOCLIST)
            for doc in SORTEDDOCLIST:
                print("doc ID: ", doc[1], " score: ", "%.4f" % doc[0])

        #TOP K 查询
        elif choice == 2:
            INPUTWORDS=preCheck_zh(STATEMENT)

            WORDSET = set(INPUTWORDS)

            DOCLIST = searchWord.searchWords(INDEX, WORDSET)
            # print(DOCLIST)
            #根据tf-idf计算分数
            #取top20
            SORTEDDOCLIST = sortDoc.TopKScore(20, INDEX, FILENUM, WORDSET, DOCLIST)
            for doc in SORTEDDOCLIST:
                print("doc ID: ", doc[1], " score: ", "%.3f" % doc[0])
        #Bool 查询
        elif choice == 3:
            INPUTWORDS=preCheck_zh(STATEMENT)

            DOCLIST = BoolSearchDel.BoolSearch(INPUTWORDS, INDEX)
            print(len(DOCLIST),"DOCs :")
            print(DOCLIST)
        #短语查询
        elif choice == 4:
            INPUTWORDS=preCheck_zh(STATEMENT)

            WORDSET = set(INPUTWORDS)

            PHRASEDOCLIST = searchWord.searchPhrase(INDEX, WORDSET, INPUTWORDS)
            if 0 == len(PHRASEDOCLIST):
                print("Doesn't find \"", INPUTWORDS, '"')
            else:
                for key in PHRASEDOCLIST:
                    print('docID: ', key, "   num: ", len(PHRASEDOCLIST[key]))
                    print('    location: ', PHRASEDOCLIST[key])
        #模糊查询
        elif choice == 5:
            list = searchWord.wildcardSearch(STATEMENT, INDEX, WORDLIST)

        elif choice == 6:
            INPUTWORDS=preCheck_zh(STATEMENT)

            WORDSET = set(INPUTWORDS)

            resultlist = searchWord.searchSynonymsWord(INDEX,INPUTWORDS[0])

        elif choice == 7:
            print(chain.Retrieve(STATEMENT,PATH))


    else:
        print("Invalid choice! Please observe these choices carefully!")
    print()

print("ByeBye!")


# establishVSM.createVSM(INDEX,WORDLIST,'test')
