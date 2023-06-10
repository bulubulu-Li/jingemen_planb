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

def getWordList_zh():
    file = open(tools.projectpath + 'wordList_zh.json', 'r',encoding='utf-8')
    wordStr = file.read()
    wordList = json.JSONDecoder().decode(wordStr)
    return wordList

# print(getWordList())