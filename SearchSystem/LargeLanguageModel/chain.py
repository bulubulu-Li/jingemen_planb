import json
import os
from Log.log import log
from langchain.prompts import PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
# from langchain.llms import ChatOpenAI as OpenAI
from langchain.chat_models import ChatOpenAI as OpenAI
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from rouge import Rouge
import SearchSystem.tools as tools

import openai as BaseOpenAI

from langchain.document_loaders.base import BaseLoader
from langchain.docstore.document import Document
from SearchSystem.DataManager import SqlDataManager, DataForm
from langchain.prompts import PromptTemplate

# 定义一个模板，用于生成问题回答的提示语
prompt_template = """
你现在是一个经验丰富，十分严谨的12345热线工作人员，负责解答市民的各种问题。现在，你会得到一份 背景知识 ，里面包括了回答市民问题所需要相关的知识。
你必须礼貌，准确，严谨，无遗漏地根据这份知识来回答用户的问题，尽量使用这份知识的原文，不要遗漏原文的每一句话。按照给的资料的顺序，在使用到参考文献的地方标出参考文献角标，如[1]。
不要列出参考文献列表。
如果你不知道答案，只回答"未找到答案"，不要编造答案。如果你的答案不是来自 背景知识 ，只回答"未找到答案"，不要根据你已有的知识回答。
你必须使用中文回答。

背景知识: {context}

问题: {question}
中文答案:"""

# 定义一个PromptTemplate对象，用于生成问题回答的提示语
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# 定义一个全局变量，用于存储OpenAI API Key
API_KEY=""

# 定义一个全局变量，用于存储OpenAIEmbeddings对象
embeddings = None

# 定义一个全局变量，用于存储CharacterTextSplitter对象
text_splitter = CharacterTextSplitter( separator = "。",chunk_size=300, chunk_overlap=0)

# 定义一个全局变量，用于存储Chroma对象
docsearch=None

# 定义一个全局变量，用于存储检索模型
chain=None

persist_directory = tools.searchSystemPath('db')

# 定义一个类，用于从数据库中加载数据
class chain_loader(BaseLoader):

    def __init__(self) -> None:
        super().__init__()

    # 从数据库中加载数据
    def load(self) -> list:
        docs = []
        datamanager=SqlDataManager()
        for item in datamanager:
            meta=item.metadata
            meta["docId"]=item.docId
            meta["title"]=item.title
            # 把none的设为""
            for key in meta:
                if meta[key] is None:
                    meta[key]=""
            doc=Document(page_content=item.title+"\n\n"+item.page_content ,metadata=meta)
            if len(doc.page_content) > 1000:
                log.info(f'{item.title} is too long, {doc}')
            # split text if filetype is doc 
            # if item["metadata"]["filetype"]=="doc":
            #     log.info(f"splitting doc {path}/{filename}")
            #     docs.extend(doc_splitter.split_documents([doc]))  
            else:
                log.info(f"splitting {item.metadata['filetype']} {item.docId}")
                docs.extend(text_splitter.split_documents([doc]))
        return docs

# 获取OpenAI API Key
def getApiKey():
    global API_KEY
    # 如果API Key以"sk-"开头，则直接返回API Key
    # 否则，从环境变量中获取API Key
    if API_KEY.startswith("sk-"):
        return API_KEY
    else:
        if os.getenv("OPENAI_API_KEY") is not None:  # 如果是在Railway上部署，需要删除代理
            log.info('Got API_KEY from env')
            log.info(os.getenv("OPENAI_API_KEY"))
            API_KEY = os.getenv("OPENAI_API_KEY")  # 如果环境变量中设置了OPENAI_API_KEY，则使用环境变量中的OPENAI_API_KEY
            return API_KEY
        else:
            log.info('请在openai官网注册账号，获取api_key填写至程序内或命令行参数中')
            exit()

# 获取文档ID
def getDocID(filename):
    end = filename.find('.')
    docId = filename[0:end]
    return int(docId)

# 初始化OpenAIEmbeddings对象和检索模型
def embedding():
    global embeddings 
    global text_splitter
    global docsearch
    global persist_directory

    # 初始化OpenAIEmbeddings对象
    embeddings = OpenAIEmbeddings(openai_api_key=getApiKey())

    # 如果不需要重新生成Chroma对象，则直接返回
    if tools.getConfig("new_embedding")==False:
        docsearch=Chroma(persist_directory=persist_directory,embedding_function=embeddings)
        return
    
    # 重新生成Chroma对象
    loader = chain_loader()
    split_docs = loader.load()
    log.info(f'embeding start, persist_directory:{persist_directory}, split_docs:{split_docs}')
    if len(split_docs) > 0:
        if docsearch is None:
            docsearch=Chroma.from_documents(split_docs,embeddings, persist_directory=persist_directory)
        else:
            docsearch.add_documents(split_docs)    

    tools.setConfig("new_embedding",False)

# 初始化检索模型
def init():
    global chain
    log.info('chain init!!!')
    if chain is None:
        log.info("chain is None,start embedding")
        embedding()
        log.info("embedding finished")
        chain_type_kwargs = {"prompt": PROMPT}
        # retrieve 5 items each time
        chain = RetrievalQA.from_chain_type(llm=OpenAI(model_name="gpt-3.5-turbo-16k-0613",max_tokens=500,temperature=0), chain_type="stuff",retriever=docsearch.as_retriever(search_kwargs={'k':5}), chain_type_kwargs=chain_type_kwargs,verbose=True,return_source_documents=True)

# 根据问题获取答案
def Retrieve(question):
    global docsearch
    global chain
    global PROMPT

    return chain({'query': question})
    # return chain._get_docs(question)

init()