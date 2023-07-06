import os
import tools
from LanguageAnalysis import stemming
import jieba
import json
from DataManager import DataForm,BaseDataManager
from langchain.document_loaders import DiffbotLoader


def preProcess(filename):
    file = open(filename, 'r')
    content = file.read()
    words = stemming.lemmatize_sentence(content, False)
    return words


def preProcess_zh_qq(dataItem:DataForm):
    return jieba.cut(dataItem.title)

def preProcess_zh_qa(dataItem:DataForm):
    return jieba.cut(dataItem.title+'\n\n'+dataItem.page_content)


def processDirectory(directname):
    path = tools.projectpath
    path += directname
    files = os.listdir(path)
    result = []
    for file in files:
        content = preProcess(path + '/' + file)
        result.append(content)
        # print(content)
    return result

# processDirectory('test')
