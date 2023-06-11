import json
import os
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

import openai as BaseOpenAI

from langchain.document_loaders.base import BaseLoader
from langchain.docstore.document import Document

from langchain.prompts import PromptTemplate
prompt_template = """
你现在是一个经验丰富，十分严谨的12345热线工作人员，负责解答市民的各种问题。现在，你会得到一份 背景知识 ，里面包括了回答市民问题所需要相关的知识。
你必须礼貌，准确，严谨，无遗漏地根据这份知识来回答用户的问题，尽量使用这份知识的原文，不要遗漏原文的每一句话。
如果你不知道答案，只回答"未找到答案"，不要编造答案。如果你的答案不是来自 背景知识 ，只回答"未找到答案"，不要根据你已有的知识回答。
你必须使用中文回答。

背景知识: {context}

问题: {question}
中文答案:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

API_KEY=""

embeddings = None
text_splitter = CharacterTextSplitter( separator = "。",chunk_size=300, chunk_overlap=0)
doc_splitter =CharacterTextSplitter(separator = "。\n\n",chunk_size=150, chunk_overlap=0)
docsearch=None
persist_directory = 'db'
chain=None

# 标准json的loader，内部完成了split text
class chain_loader(BaseLoader):

    def __init__(self) -> None:
        super().__init__()
    def load(self, path: str) -> list:
        docs = []
        for filename in os.listdir(path=path):
            # skip folder
            if os.path.isdir(f'{path}/{filename}'):
                continue
            f = open(f'{path}/{filename}', 'r',encoding='utf-8')
            content = json.load(f)
            # for each item in content, generate a doc
            for item in content:
                doc=Document(page_content=item["page_content"] ,metadata=item["metadata"])
                if len(doc.page_content) > 1000:
                    print(f'{path}/{filename} is too long, {doc}')
                # split text if filetype is doc 
                if item["metadata"]["filetype"]=="doc":
                    print(f"splitting doc {path}/{filename}")
                    docs.extend(doc_splitter.split_documents([doc]))  
                else:
                    print(f"splitting {item['metadata']['filetype']} {path}/{filename}")
                    docs.extend(text_splitter.split_documents([doc]))

        return docs

def getApiKey():
    global API_KEY
    # if api_key start with "sk-" return apikey
    # else return None
    if API_KEY.startswith("sk-"):
        return API_KEY
    else:
        if os.getenv("OPENAI_API_KEY") is not None:  # 如果是在Railway上部署，需要删除代理
            print('Got API_KEY from env')
            print(os.getenv("OPENAI_API_KEY"))
            API_KEY = os.getenv("OPENAI_API_KEY")  # 如果环境变量中设置了OPENAI_API_KEY，则使用环境变量中的OPENAI_API_KEY
            return API_KEY
        else:
            print('请在openai官网注册账号，获取api_key填写至程序内或命令行参数中')
            exit()

def getDocID(filename):
    end = filename.find('.')
    docId = filename[0:end]
    return int(docId)

def embedding(path):
    global embeddings 
    global text_splitter
    global docsearch
    global persist_directory
    
    embeddings = OpenAIEmbeddings(openai_api_key=getApiKey())
    loader = chain_loader()
    split_docs = loader.load(path)
    print(f'embeding start')
    if len(split_docs) > 0:
        if docsearch is None:
            docsearch=Chroma.from_documents(split_docs,embeddings, persist_directory=persist_directory)
        else:
            docsearch.add_documents(split_docs)    

def Retrieve(question,path):
    global docsearch
    global chain
    global PROMPT
    if chain is None:
        print("chain is None,start embedding")
        embedding(path)
        print("embedding finished")
        chain_type_kwargs = {"prompt": PROMPT}
        chain = RetrievalQA.from_chain_type(llm=OpenAI(model_name="gpt-3.5-turbo",max_tokens=500,temperature=0), chain_type="stuff", retriever=docsearch.as_retriever(), chain_type_kwargs=chain_type_kwargs,verbose=True,return_source_documents=True)

    return chain({'query': question})
