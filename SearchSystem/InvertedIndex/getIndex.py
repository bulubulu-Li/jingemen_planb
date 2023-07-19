import json
import SearchSystem.tools as tools

def getIndex():
    file = open(tools.searchsystempath + 'invertIndex.json', 'r')
    indexStr = file.read()
    index = json.JSONDecoder().decode(indexStr)
    return index

def getWordList():
    file = open(tools.searchsystempath + 'wordList.json', 'r')
    wordStr = file.read()
    wordList = json.JSONDecoder().decode(wordStr)
    return wordList

def getIndex_zh():
    return tools.readFile_zh('invertIndex_zh.json','index')

def getIndex_zh_qq():
    return tools.readFile_zh('invertIndex_zh_qq.json', 'index')
    
def getIndex_zh_qa():
    return tools.readFile_zh('invertIndex_zh_qa.json', 'index')

def getWordList_zh():
    return tools.readFile_zh('wordList_zh.json','index')

def getWordList_zh_qq():
    return tools.readFile_zh('wordList_zh_qq.json', 'index')

def getWordList_zh_qa():
    return tools.readFile_zh('wordList_zh_qa.json', 'index')

def getWordCount_zh():
    return tools.readFile_zh('wordCount_zh.json', 'index')

def getWordCount_zh_qq():
    return tools.readFile_zh('wordCount_zh_qq.json', 'index')

def getWordCount_zh_qa():
    return tools.readFile_zh('wordCount_zh_qa.json', 'index')

# print(getWordList())