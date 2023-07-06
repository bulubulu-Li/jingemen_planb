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
import tools


class DocIdManager:
    """
    用于管理docid的各种变换
    """
    docOffset:int

    def __init__(self,offset:int):
        if not isinstance(offset,int):
            raise TypeError("DocIdManager的参数必须是int")
        if offset<10000:
            self.docOffset=10000
        else:
            self.docOffset=10**int(math.log10(offset)+2)
    
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
    page_content:str
    title:str
    docId:int
    metadata:dict
    questions:list[str]
    docIdManager:DocIdManager
    


    def __init__(self,dict:dict,idManager:DocIdManager) -> None:
        if not isinstance(dict,dict):
            raise TypeError("DataForm的参数必须是dict")
        
        if not 'page_content' in dict:
            raise KeyError("DataForm的参数必须包含page_content")
        if not 'title' in dict:
            raise KeyError("DataForm的参数必须包含title")
        if not 'doc ID' in dict:
            raise KeyError("DataForm的参数必须包含doc ID")
        if not 'metadata' in dict:
            raise KeyError("DataForm的参数必须包含metadata")
        if not 'questions' in dict:
            raise KeyError("DataForm的参数必须包含questions")
        
        if not isinstance(idManager,DocIdManager):
            raise TypeError("DataForm的参数offset必须是str")
        if not isinstance(dict['page_content'],str):
            raise TypeError("DataForm的参数page_content必须是str")
        if not isinstance(dict['title'],str):
            raise TypeError("DataForm的参数title必须是str")
        if not isinstance(dict['doc ID'],int):
            raise TypeError("DataForm的参数doc ID必须是int")
        if not isinstance(dict['metadata'],dict):
            raise TypeError("DataForm的参数metadata必须是dict")
        if not isinstance(dict['questions'],list):
            raise TypeError("DataForm的参数questions必须是list")

        self.page_content=dict['page_content']
        self.title=dict['title']
        self.docId=dict['doc ID']
        self.metadata=dict['metadata']
        self.questions=dict['questions']
        self.docOffset=idManager

    @property
    def docId_qa(self):
        return self.docIdManager.get_qa_id(self.docId)
    
    @property
    def docId_qq(self):
        return self.docIdManager.get_qq_id(self.docId)

class BaseDataManager(ABC,DocIdManager):
    """
    一个基础版本的数据管理器，用于规范数据管理器的接口
    """
    folder:str
    data:list[DataForm]
    pointer:int
    len:int

    def __init__(self):
        self.folder=os.path.join(tools.projectpath,'pairs')
        self.data=[]
        self.pointer=0
        # 读取这个文件夹中的json文件
        docList=[int(x.split('.')[0]) for x in os.listdir(os.path.join(self.folder,'pairs')) if x.endswith(".json")]
        # 排序保证每次拿到的顺序都一样
        docList.sort()
        for file in docList:
            with open(os.path.join(self.folder,str(file)+".json"),'r',encoding='utf-8') as f:
                self.data.extend(json.load(f))
        self.len=len(self.data)
        DocIdManager.__init__(self,self.len)
    
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
        docId=self.docIdManager.get_docId(docId)
        return DataForm(self.data[docId],DocIdManager(self.len))
    
    def __len__(self)->int:
        return self.len
    