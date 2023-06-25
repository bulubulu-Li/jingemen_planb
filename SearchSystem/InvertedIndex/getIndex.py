import json
import tools

def getIndex():
    file = open(tools.projectpath + 'invertIndex.json', 'r')
    indexStr = file.read()
    index = json.JSONDecoder().decode(indexStr)
    return index

def getWordList():
    file = open(tools.projectpath + 'wordList.json', 'r')
    wordStr = file.read()
    wordList = json.JSONDecoder().decode(wordStr)
    return wordList

def getIndex_zh():
    file = open(tools.projectpath + 'invertIndex_zh.json', 'r',encoding='utf-8')
    indexStr = file.read()
    index = json.JSONDecoder().decode(indexStr)
    return index

def getIndex_zh_qq():
    file = open(tools.projectpath + 'invertIndex_zh_qq.json', 'r',encoding='utf-8')
    indexStr = file.read()
    index = json.JSONDecoder().decode(indexStr)
    return index

def getIndex_zh_qa():
    file = open(tools.projectpath + 'invertIndex_zh_qa.json', 'r',encoding='utf-8')
    indexStr = file.read()
    index = json.JSONDecoder().decode(indexStr)
    return index

def getWordList_zh():
    file = open(tools.projectpath + 'wordList_zh.json', 'r',encoding='utf-8')
    wordStr = file.read()
    wordList = json.JSONDecoder().decode(wordStr)
    return wordList

def getWordList_zh_qq():
    file = open(tools.projectpath + 'wordList_zh_qq.json', 'r',encoding='utf-8')
    wordStr = file.read()
    wordList = json.JSONDecoder().decode(wordStr)
    return wordList

def getWordList_zh_qa():
    file = open(tools.projectpath + 'wordList_zh_qa.json', 'r',encoding='utf-8')
    wordStr = file.read()
    wordList = json.JSONDecoder().decode(wordStr)
    return wordList

def getWordCount_zh():
    file = open(tools.projectpath + 'wordCount_zh.json', 'r',encoding='utf-8')
    wordStr = file.read()
    wordCount = json.JSONDecoder().decode(wordStr)
    return wordCount

def getWordCount_zh_qq():
    file = open(tools.projectpath + 'wordCount_zh_qq.json', 'r',encoding='utf-8')
    wordStr = file.read()
    wordCount = json.JSONDecoder().decode(wordStr)
    return wordCount

def getWordCount_zh_qa():
    file = open(tools.projectpath + 'wordCount_zh_qa.json', 'r',encoding='utf-8')
    wordStr = file.read()
    wordCount = json.JSONDecoder().decode(wordStr)
    return wordCount

# print(getWordList())