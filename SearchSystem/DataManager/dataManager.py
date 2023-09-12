"""
这个模块的目的是为了将数据从数据库中取出来，是一层对于业务层和底层数据存储方式的隔离

首先，我们需要考虑业务到底需要对底层数据使用什么操作？
底层数据的例子如下：
[
    {
        "page_content": "若您有携号转网服务需求时，可通过短信、营业厅、客服热线等渠道先向携出方查询号码是否满足携转条件。     若核查不满足携号条件的，您可针对不满足条件的原因、携号转网后受影响的业务问题，按您本人意愿考虑保留原有业务或解除，即确定继续使用或携出。     若核查满足携转条件的，您可发送短信获取携号转网授权码，但需在授权码有效期内携带有效身份证件前往携入方申请办理携入，携入方会为您提供新的移动电话卡。    办理流程：    第一步、编辑短信CXXZ#姓名#身份证号，发送至10086，查询其电话号码是否满足符合携号转网条件。    第二步、如不符合携号转网条件，需根据查询结果，与携出方达成携出的条件。    第三步、查询结果满足携号转网条件，编辑短信SQXZ#姓名#身份证号，发送至10086，获取携号转网授权码。    第四步、客户在收到授权码后,需在授权码有效时间内携本人身份证到携入方号码归属地的自有实体营业厅办理。携入方收到成功的生效结果告知后激活号码，实现携入号码正式入网。",
        "title": "如何办理携号转网/携号转网办理流程？",
        "doc ID": 0,
        "metadata": {
            "url": "https://www.jingmen.gov.cn/col/col18658/index.html?kinfoGuid=5564ba85-a1f0-424c-b691-f7dd3919e74e",
            "filetype": "json"
        },
        "questions": [
            "我应该怎么办理携号转网"
        ]
    },
    ...
]
需要的功能有：
1. 指定数据源（对于一组特定的数据源，保证每次同一条目的id相同）（init函数）
2. 逐条遍历所有的数据（用于构建index，逐条提问）（迭代器）
3. 展示一个id的文件的信息，即随机查找
"""
from abc import ABC, abstractmethod
import math
import os
import json
from typing import Any
import SearchSystem.tools as tools
from Log.log import log
from SearchSystem.DataManager.mysql_helper import MysqlHelper
from collections import OrderedDict

class DocIdManager:
    """
    用于管理docid的各种变换
    """
    def __init__(self, offset: int):
        if not isinstance(offset, int):
            raise TypeError("DocIdManager的参数必须是int")
        if offset < 10000:
            offset = 10000
        else:
            offset = 10 ** int(math.log10(offset) + 2)
        self.docOffset = offset

    def get_qa_id(self,docId:int)->int:
        return docId+self.docOffset
    
    def get_qq_id(self,docId:int)->int:
        return docId+self.docOffset*2
    
    def get_method(self,docId:int)->str:
        if docId//self.docOffset==1:
            return "qa"
        elif docId//self.docOffset==2:
            return "qq"
    
    def get_docId(self,id:int)->int:
        return id%self.docOffset

class DataForm:
    """
    用于规范数据的格式
    - page_content:str
    - title:str
    - docId:int
    - metadata:dict
    - questions:list[str]
    - docIdManager:DocIdManager
    {
        "page_content": "学校在校外实践基地开展研学活动是按照省、市关于组织中小学生开展研学实践教育活动的有关要求进行的，是年度教育教学工作的重要内容之一。",
        "title": "校外实践基地开展研学活动符合政策吗",
        "doc ID": 98,
        "metadata": {
            "url": "https://www.jingmen.gov.cn/col/col18658/index.html?kinfoGuid=8ab50925-8809-4a61-b236-34ea1a86655c",
            "filetype": "json"
        },
        "questions": [
            "在校外基地开展研学活动可以吗？"
        ]
    }
    """
    # page_content:str
    # title:str
    # docId:int
    # metadata:dict
    # questions:list[str]
    docIdManager:DocIdManager
    


    def __init__(self,dic:dict,idManager:DocIdManager) -> None:
        if not isinstance(dic,dict):
            raise TypeError("DataForm的参数必须是dict")
        
        if not 'page_content' in dic:
            raise KeyError("DataForm的参数必须包含page_content")
        if not 'title' in dic:
            raise KeyError("DataForm的参数必须包含title")
        if not 'doc ID' in dic:
            raise KeyError("DataForm的参数必须包含doc ID")
        if not 'metadata' in dic:
            raise KeyError("DataForm的参数必须包含metadata")
        if not 'questions' in dic:
            raise KeyError("DataForm的参数必须包含questions")
        
        if not isinstance(idManager,DocIdManager):
            raise TypeError("DataForm的参数offset必须是str")
        if not isinstance(dic['page_content'],str):
            raise TypeError("DataForm的参数page_content必须是str")
        if not isinstance(dic['title'],str):
            raise TypeError("DataForm的参数title必须是str")
        if not isinstance(dic['doc ID'],int):
            raise TypeError("DataForm的参数doc ID必须是int")
        if not isinstance(dic['metadata'],dict):
            raise TypeError("DataForm的参数metadata必须是dict")
        if not isinstance(dic['questions'],list):
            raise TypeError("DataForm的参数questions必须是list")

        self.page_content=dic['page_content']
        self.title=dic['title']
        self.docId=dic['doc ID']
        self.metadata=dic['metadata']
        self.questions=dic['questions']
        self.docIdManager=idManager

    @property
    def docId_qa(self):
        return self.docIdManager.get_qa_id(self.docId)
    
    @property
    def docId_qq(self):
        return self.docIdManager.get_qq_id(self.docId)
    
    def __str__(self):
            return "DataForm(page_content={}, title={}, docId={}, metadata={}, questions={})".format(self.page_content, self.title, self.docId, self.metadata, self.questions)

class BaseDataManager(DocIdManager):
    """
    一个基础版本的数据管理器，用于规范数据管理器的接口
    """
    """
    一个基础版本的数据管理器，用于规范数据管理器的接口
    """
    folder:str=os.path.join(tools.searchsystempath,'pairs')
    data:list[DataForm] = []
    len:int = 0
    pointer:int  # 这个将作为实例变量

    def __init__(self):
        # 只有在data为空时，我们才从文件夹读取json文件
        if not BaseDataManager.data:
            # 读取这个文件夹中的json文件
            docList=[int(x.split('.')[0]) for x in os.listdir(BaseDataManager.folder) if x.endswith(".json")]
            log.info(docList)
            # 排序保证每次拿到的顺序都一样
            docList.sort()
            for file in docList:
                with open(os.path.join(BaseDataManager.folder,str(file)+".json"),'r',encoding='utf-8') as f:
                    BaseDataManager.data.extend(json.load(f))
            BaseDataManager.len=len(BaseDataManager.data)
            DocIdManager.__init__(self,BaseDataManager.len)

        self.pointer = 0  # 每个实例都有自己独立的pointer

    # def __init__(self):
    #     self.data=[]
    #     self.pointer=0
    #     # 读取这个文件夹中的json文件
    #     docList=[int(x.split('.')[0]) for x in os.listdir(self.folder) if x.endswith(".json")]
    #     log.info(docList)
    #     # 排序保证每次拿到的顺序都一样
    #     docList.sort()
    #     for file in docList:
    #         with open(os.path.join(self.folder,str(file)+".json"),'r',encoding='utf-8') as f:
    #             self.data.extend(json.load(f))
    #     self.len=len(self.data)
    #     DocIdManager.__init__(self,self.len)
    
    def __iter__(self):
        return self
    
    def __next__(self)->DataForm:
        """
        迭代器的实现
        """
        if self.pointer<self.len:
            self.pointer+=1
            return DataForm(self.data[self.pointer-1],DocIdManager(self.len))
        else:
            raise StopIteration
        
    def __getitem__(self, docId:int)->DataForm:
        """
        随机获取指定docId的内容
        """        
        docId=self.get_docId(docId)
        return DataForm(self.data[docId],DocIdManager(self.len))
    
    def __len__(self)->int:
        return self.len
    
    def show(self):
        return self.data

class SqlDataManager(DocIdManager):
    len = None
    mysqlHelper = None
    data = None
    
    def __new__(cls):
        if cls.mysqlHelper is None:
            cls.update()
        return super().__new__(cls)
    
    @classmethod
    def update(cls):
        # 先缓存原来的值

        try:
            # 尝试获取新的值
            new_mysqlHelper=MysqlHelper(config=tools.getMysqlConfig())
            new_len=new_mysqlHelper.search("SELECT COUNT(*) FROM knowledgepair WHERE state=10002")[0][0]
            data = new_mysqlHelper.searchDict("SELECT * FROM knowledgepair WHERE state=10002")
            log.info(f"SqlDataManager update: {data}")
            new_data=[DataForm({
                "page_content": x['answer'],
                "title": x['question'],
                "doc ID": int(x['id']),
                "metadata": {
                    "filetype": "json",
                    "keyWord": x['keyWord'],
                    "from": x['from'],
                    "fromId": x['fromId'],
                    "state": x['state'],
                    "isValid": x['isValid'],
                    "isDeleted": x['isDeleted']
                },
                "questions": []
            }, DocIdManager(new_len)) for x in data]
            print('finish')
            log.info(f"SqlDataManager update success")
            cls.mysqlHelper = new_mysqlHelper
            cls.len = new_len
            cls.data = OrderedDict([(x.docId, x) for x in new_data])
        except Exception as e:
            # 如果获取新的值失败，则恢复原来的值
            log.warning(f"SqlDataManager update failed: {e}")

    def __init__(self):
        self.pointer = 1
        super().__init__(SqlDataManager.len)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        """
        迭代器的实现
        """
        if self.pointer <= self.len:
            self.pointer += 1
            item = list(SqlDataManager.data.values())[self.pointer - 2]
            log.info(f"SqlDataManager __next__ success: {item}")
            return item
        else:
            raise StopIteration
        
    def __getitem__(self, docId:int):
        """
        随机访问获取指定docId的内容
        """        
        docId = self.get_docId(docId)
        log.info(f"SqlDataManager __getitem__ success: {SqlDataManager.data[docId]}")
        return SqlDataManager.data[docId]
    
    def __len__(self):
        return SqlDataManager.len
    
    def show(self):
        return SqlDataManager.data