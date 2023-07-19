import os
import SearchSystem.tools as tools
from SearchSystem.LanguageAnalysis import stemming
import jieba
import json
from SearchSystem.DataManager import DataForm,BaseDataManager
from langchain.document_loaders import DiffbotLoader


def preProcess(filename):
    file = open(filename, 'r')
    content = file.read()
    words = stemming.lemmatize_sentence(content, False)
    return words


def preProcess_zh_qq(dataItem:DataForm):
    return list(jieba.cut(dataItem.title))

def preProcess_zh_qa(dataItem:DataForm):
    return list(jieba.cut(dataItem.title+'\n\n'+dataItem.page_content))


def processDirectory(directname):
    path = tools.searchsystempath
    path += directname
    files = os.listdir(path)
    result = []
    for file in files:
        content = preProcess(path + '/' + file)
        result.append(content)
        # print(content)
    return result

# processDirectory('test')
