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
from SearchSystem.InvertedIndex import getIndex
from SearchSystem.LanguageAnalysis import stemming
from SearchSystem.Serching import searchWord
# from SearchSystem.SpellingCorrect import spell
from SearchSystem.scoreQuery import sortDoc
from SearchSystem.BoolSearch import BoolSearchDel
from SearchSystem.InvertedIndex import establishIndex
from SearchSystem.LargeLanguageModel import chain
from SearchSystem.DataManager import SqlDataManager, DataForm
from apscheduler.schedulers.background import BackgroundScheduler
import jieba
from rouge import Rouge

def preCheck_zh(statement):
    # log.info("分词...")
    inputwords = jieba.cut(statement)
    return inputwords

def check_expect(doclist, expectlist):
    # log.info("check_expect...")
    res = []
    docs = [x[1] for x in doclist]
    for i, doc in enumerate(docs):
        if doc in expectlist:
            res.append(doclist[i])
            res[-1].append(i)
    return res

class SearchIndex():
    # 涉及搜索所需要的索引、数据都存在这个类里面，如WORDLIST、INDEX_QQ等，都存在这里。
    # 用self.word_list、self.index_qq来存储
    def __init__(self, config):
        self.config = config

        self.load()
    
    def load(self):
        # 创建index
        establishIndex.createIndex_zh()
        self.manager = SqlDataManager()
        log.info("getting word list...")
        self.WORDLIST = getIndex.getWordList_zh()

        # 载入index
        log.info("getting index...")
        self.index = getIndex.getIndex_zh()
        self.INDEX_QQ = getIndex.getIndex_zh_qq()
        self.INDEX_QA = getIndex.getIndex_zh_qa()

        # 在载入词汇表
        log.info("loading the wordnet...")
        self.WORDCOUNT = getIndex.getWordCount_zh()
        self.WORDCOUNT_QQ = getIndex.getWordCount_zh_qq()
        self.WORDCOUNT_QA = getIndex.getWordCount_zh_qa()
        pass

    def get_config(self):
        return self.config

    def get_word_list(self):
        return self.WORDLIST

    def get_index(self):
        return self.index

    def get_index_qq(self):
        return self.INDEX_QQ

    def get_index_qa(self):
        return self.INDEX_QA

    def get_word_count(self):
        return self.WORDCOUNT

    def get_word_count_qq(self):
        return self.WORDCOUNT_QQ

    def get_word_count_qa(self):
        return self.WORDCOUNT_QA
    
    def get_manager(self):
        return self.manager

    def filenum(self):
        return self.manager.len

class SearchSyetem():
    def __init__(self, config):
        # 类初始化
        self.config = config
        self.index = SearchIndex(config)
        self.blockList=[]

        # 直接定义一个定时器
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.update, 'interval', hours=24)
        scheduler.start()
    
    def update(self):
        # 数据库更新
        SqlDataManager.update()
        tools.setConfig("establishIndex", True)
        search_index = SearchIndex()
        self.index = search_index
        self.blockList=[]


    def search(self, statement, choice=1, loop=False, expectList=[]):
        source = []
        log.info(f"choice: {choice}" )
        # 倒排全部查找
        if choice == 1:
            inputwords = preCheck_zh(statement)

            wordset = set(inputwords)

            DOCLIST = searchWord.searchWords(self.index.get_index(), wordset)
            sortedDocList = sortDoc.TopKScore(40, self.index.get_index(), self.index.filenum(), wordset, DOCLIST, self.index.get_word_count())
            # exclude blockList
            sortedDocList = [x for x in sortedDocList if x[1] not in self.blockList]
            # log.info(sortedDocList)
            source = check_expect(sortedDocList, expectList)
            # log.info(sortedDocList)
            if loop == False:
                return sortedDocList, source
            for doc in sortedDocList:
                log.info(f"doc ID: {tools.showDocID(doc[1])} score: {doc[0]:.3f}" )

        # 倒排qq查找
        if choice == 2:
            inputwords = preCheck_zh(statement)

            wordset = set(inputwords)

            DOCLIST = searchWord.searchWords(self.index.get_index_qq(), wordset)
            sortedDocList = sortDoc.TopKScore(40, self.index.get_index_qq(), self.index.filenum(), wordset, DOCLIST, self.index.get_word_count_qq())
            sortedDocList = [x for x in sortedDocList if x[1] not in self.blockList]
            source = check_expect(sortedDocList, expectList)
            if loop == False:
                return sortedDocList, source
            for doc in sortedDocList:
                log.info(f"doc ID: {tools.showDocID(doc[1])} score: {doc[0]:.3f}" )

        # 倒排qa查找
        if choice == 3:
            inputwords = preCheck_zh(statement)

            wordset = set(inputwords)

            DOCLIST = searchWord.searchWords(self.index.get_index_qa(), wordset)
            sortedDocList = sortDoc.TopKScore(40, self.index.get_index_qa(), self.index.filenum(), wordset, DOCLIST, self.index.get_word_count_qa())
            sortedDocList = [x for x in sortedDocList if x[1] not in self.blockList]
            source = check_expect(sortedDocList, expectList)
            if loop == False:
                return sortedDocList, source
            for doc in sortedDocList:
                log.info(f"doc ID: {tools.showDocID(doc[1])} score: {doc[0]:.3f}" )

        # qq qa 各召回一部分
        if choice == 4:
            inputwords = preCheck_zh(statement)

            wordset = set(inputwords)

            DOCLIST_QQ = searchWord.searchWords(self.index.get_index_qq(), wordset)
            SORTEDDOCLIST_QQ = sortDoc.TopKScore(20, self.index.get_index_qq(), self.index.filenum(), wordset, DOCLIST_QQ, self.index.get_word_count_qq())

            DOCLIST_QA = searchWord.searchWords(self.index.get_index_qa(), wordset)
            SORTEDDOCLIST_QA = sortDoc.TopKScore(20, self.index.get_index_qa(), self.index.filenum(), wordset, DOCLIST_QA, self.index.get_word_count_qa())

            sortedDocList = SORTEDDOCLIST_QQ + SORTEDDOCLIST_QA
            sortedDocList = [x for x in sortedDocList if x[1] not in self.blockList]
            sortedDocList = sorted(sortedDocList, key=lambda x: x[0], reverse=True)

            source = check_expect(sortedDocList, expectList)
            if loop == False:
                return sortedDocList, source


        elif choice == 7:
            retrieve_res = chain.Retrieve(statement)
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
            docList = []
            # 如果result包含“未找到答案”，直接返回
            if "未找到答案" in retrieve_res["result"]:
                return answer, []
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

                max_score_index = tmp_score.index(max(tmp_score))
                if max_score_index not in source:
                    source.append(max_score_index)
                    docList.append(retrieve_res["source_documents"][max_score_index])

            log.info(f"docList: {docList}")
            if loop == False:
                return answer, docList
            # log.info(chain.Retrieve(statement, PATH))

    def searchResults(self,statement, choice=1, loop=False, expectList=[]):
        """
        
        当不是embeding模式的时候返回一个返回值，这个返回值是一个文档列表
        当是embedding模式的时候，返回三个返回值，分别为生成的结果，参考文献列表和对应的片段。

        """
        manager=self.index.get_manager()
        searchRes, _ = self.search(statement, choice, loop, expectList)
        docList = []
        if choice != 7:
            for x in searchRes:
                if manager.get_docId(x[1]) not in docList:
                    docList.append(manager.get_docId(x[1]))
            if len(docList) > 3:
                docList = docList[:3]

            res = [manager[x] for x in docList]
            log.info(f"docList: {[docList]}" )
            log.info(f"searchResults titles: {[x.title for x in res]}" )
            return res
        
        else:

            result,docList=self.search(statement, choice)

            return result,[manager[int(x.metadata["docId"])] for x in docList],[x.page_content for x in docList]
        
    def block(self,bList:list[int]):
        log.info(f"block: {bList}" )
        self.blockList.extend(bList)


if __name__ == "__main__":
    config = {}
    search_system = SearchSyetem(config)
    print(search_system.search("腾讯会议与用户初次相遇是在什么时候？"))