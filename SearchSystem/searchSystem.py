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
import numpy as np

class TokenDistance():
    def __init__(self, idf_path):
        idf_dict = {}
        tmp_idx_list = []
        with open(idf_path, encoding="utf8") as f:
            for line in f:
                ll = line.strip().split(" ")
                idf_dict[ll[0]] = float(ll[1])
                tmp_idx_list.append(float(ll[1]))
        self._idf_dict = idf_dict
        self._median_idf = np.median(tmp_idx_list)
    
    def predict_jaccard(self, q1, q2):
        # jaccard距离，根据idf加权
        if len(q1) < 1 or len(q2) < 1:
            return 0
        if type(q1) == str:
            q1 = set(list(jieba.cut(q1)))
        # q2不是list，而是一个字符串
        if type(q2) == str:
            q2 = set(list(jieba.cut(q2)))
        print(q1.intersection(q2))
        print(q1.union(q2))

        numerator = sum([self._idf_dict.get(word, self._median_idf) for word in q1.intersection(q2)])
        denominator  = sum([self._idf_dict.get(word, self._median_idf) for word in q1.union(q2)])
        return numerator / denominator

    def predict_left(self, q1, q2):
        # 单向相似度，分母为q1，根据idf加权
        if len(q1) < 1 or len(q2) < 1:
            return 0
        
        if type(q1) == str:
            q1 = set(list(jieba.cut(q1)))
        if type(q2) == str:
            q2 = set(list(jieba.cut(q2)))

        numerator = sum([self._idf_dict.get(word, self._median_idf) for word in q1.intersection(q2)])
        denominator  = sum([self._idf_dict.get(word, self._median_idf) for word in q1])
        return numerator / denominator

    def predict_cqrctr(self, q1, q2):
        # cqr*ctr
        if len(q1) < 1 or len(q2) < 1:
            return 0

        cqr = self.predict_left(q1, q2)
        ctr = self.predict_left(q2, q1)

        return cqr * ctr
    
    def filter(self,query,sortedDocList):
        temp=[[doc[0],doc[1],doc[2],{
            "jaccard":self.predict_jaccard(query,set([x['word'] for x in doc[2]['word_list']])),
            "cqrctr":self.predict_cqrctr(query,set([x['word'] for x in doc[2]['word_list']])),
            "left":self.predict_left(query,set([x['word'] for x in doc[2]['word_list']]))
        }] for doc in sortedDocList]
        # filt by the score of jaccard cqrctr and left, require all of them to be larger than 0.25
        temp=[x for x in temp if x[3]['jaccard']>0.25 and x[3]['cqrctr']>0.25 and x[3]['left']>0.25]
        return temp


def preCheck_zh(statement):
    # log.info("分词...")
    inputwords = jieba.cut(statement)
    # print(f'in precheck: {set(list(inputwords))}')
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
    def __init__(self, config={}):
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
        return len(self.manager)

class SearchSystem():
    def __init__(self, config={}):
        # 类初始化
        # self.config = config
        # self.index = SearchIndex(config)
        # self.blockList=[]
        self.update()
        # TODO 处理文件
        self.token_distance = TokenDistance("./idf.txt")

        # 直接定义一个定时器
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.update, 'interval', hours=24)
        scheduler.start()
        log.info("=================Searching System=================")
    
    def update(self):
        # 数据库更新
        SqlDataManager.update()
        tools.setConfig("establishIndex", True)
        tools.setConfig("new_embedding", False)
        search_index = SearchIndex()
        self.index = search_index
        self.blockList=[]


    def search(self, statement, choice=1, loop=False, expectList=[]):
        source = []
        log.info(f"choice: {choice}, statement {statement}" )
        # 倒排全部查找
        if choice == 1:
            inputwords = preCheck_zh(statement)

            wordset = set(inputwords)

            DOCLIST = searchWord.searchWords(self.index.get_index(), wordset)
            sortedDocList = sortDoc.TopKScore(40, self.index.get_index(), self.index.filenum(), wordset, DOCLIST, self.index.get_word_count())
            # exclude blockList
            # print(f'sortedDocList {sortedDocList}, DOCLIST {DOCLIST},wordset {wordset},index {self.index.get_index()},filenum {self.index.filenum()},wordcount {self.index.get_word_count()}')
            sortedDocList = [x for x in sortedDocList if x[1] not in self.blockList]
            source = check_expect(sortedDocList, expectList)
            sortedDocList = self.token_distance.filter(statement, sortedDocList)
            print(sortedDocList)
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
        searchRes, tempdoclist = self.search(statement, choice, loop, expectList)
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

            result,docList=searchRes, tempdoclist

            return result,[manager[int(x.metadata["docId"])] for x in docList],[x.page_content for x in docList]
        
    def block(self,bList:list[int]):
        log.info(f"block: {bList}" )
        self.blockList.extend(bList)


if __name__ == "__main__":
    config = {}
    search_system = SearchSystem(config)
    print(search_system.search("腾讯会议与用户初次相遇是在什么时候？"))