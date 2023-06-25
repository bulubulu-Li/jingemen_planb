import os
import tools
from LanguageAnalysis import stemming
import jieba
import json


def preProcess(filename):
    file = open(filename, 'r')
    content = file.read()
    words = stemming.lemmatize_sentence(content, False)
    return words


def preProcess_qq_zh(filename):
    # if file is empty, return []
    if os.path.getsize(filename) == 0:
        return []
        
    file = open(filename, 'r', encoding='utf-8')
    content = json.load(file)
    words=[]
    for page in content:
        words+=jieba.cut(page["title"])
    return words

def preProcess_qa_zh(filename):
    # if file is empty, return []
    if os.path.getsize(filename) == 0:
        return []
        
    file = open(filename, 'r', encoding='utf-8')
    content = json.load(file)
    words=[]
    for page in content:
        words+=jieba.cut(page["page_content"])
    return words


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
