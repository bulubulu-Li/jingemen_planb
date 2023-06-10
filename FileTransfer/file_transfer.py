
import json


import os

from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader

from langchain.docstore.document import Document

# 处理哪些文本

projectpath = os.getcwd()
projectpath = projectpath.replace('/',"\\")
projectpath += "\\"
reuterspath = projectpath.replace("FileTransfer","Reuters_zh")
print( reuterspath)
FOLD_LIST=["doc","pdf","wx","json"]
counter=1

def get_path(fileType):
    return f'content/{fileType}'

def get_file_path(fileType,fileName):
    return f'content/{fileType}/{fileName}'

def store_file(content):
    global counter
    # add metadata "doc ID"=counter into every item of content
    for item in content:
        item["metadata"]["doc ID"]=counter
    filename=f'{counter}.json'
    counter+=1
    # transfer content into json
    content=json.dumps(content,ensure_ascii=False)
    with open(reuterspath+filename, 'w',encoding='utf-8') as f:
        f.write(content)
    return filename

def transfer_doc():
    path=get_path("doc")
    for filename in os.listdir(path=path):
        print(f"transfering doc {filename}")
        content=[]
        loader=Docx2txtLoader(get_file_path("doc",filename))
        pages = loader.load()
        for page in pages:
            content.append({
                "page_content":page.page_content,
                "metadata":page.metadata
            })
        filename=store_file(content)

def transfer_pdf():
    path=get_path("pdf")
    for filename in os.listdir(path=path):
        print(f"transfering pdf {filename}")
        content=[]
        loader=PyPDFLoader(get_file_path("pdf",filename))
        pages = loader.load()
        for page in pages:
            content.append({
                "page_content":page.page_content,
                "metadata":page.metadata
            })
        filename=store_file(content)

def transfer_wx():
    path=get_path("wx")
    for filename in os.listdir(path=path):
        print(f"transfering wx {filename}")
        content=[]
        with open(get_file_path("wx",filename), 'r',encoding='utf-8') as f:
            # load f as json
            json_text=json.load(f)
            content.append({
                "page_content":json_text["content"],
                "metadata":{
                    "url":json_text["url"],
                    "title": "wx/"+filename,
                }
            })
        filename=store_file(content)

def transfer_json():
    path=get_path("json")
    for filename in os.listdir(path=path):
        print(f"transfering json {filename}")
        content=[]
        with open(get_file_path("json",filename), 'r',encoding='utf-8') as f:
            # load f as json
            json_text=json.load(f)
            for item in json_text['custom']['infoList']:
                content.append({
                    "page_content":item['kinfoName']+'\n\n'+item['kinfoContent'],
                    "metadata":{
                        "url":"https://www.jingmen.gov.cn/col/col18658/index.html?kinfoGuid="+item['kinfoGuid'],
                        "title": "json/"+filename,
                    }
                })
        filename=store_file(content)

def run():
    for fold in FOLD_LIST:
        if fold=="doc":
            transfer_doc()
        elif fold=="pdf":
            transfer_pdf()
        elif fold=="wx":
            transfer_wx()
        elif fold=="json":
            transfer_json()

run()