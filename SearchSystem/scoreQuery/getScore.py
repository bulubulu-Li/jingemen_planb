import cmath
from Log.log import log
def get_tfidf(index, fileNum , docID, word) :
    docID = str(docID)
    if docID not in index[word]:
        return "0"
    tf = len(index[word][docID])
    df = len(index[word])
    idf = cmath.log10(fileNum / df).real
    if idf<0:
        idf=0
    return tf * idf

def get_wfidf(index, fileNum, docID, word):
    docID = str(docID)
    if docID not in index[word]:
        return "0"
    tf = len(index[word][docID])
    df = len(index[word])
    wf = 1 + cmath.log10(tf).real
    idf = cmath.log10(fileNum / df).real
    if idf<0:
        idf=0
    return wf * idf

def get_wfidf_Score(index,fileNum,docID,wordList,wordCount):
    score = 0
    docID = str(docID)
    # [0,0,{"score":0,"word_list":[{"word":word,"tf":tf,"df":df,"wf":wf,"idf":idf,"score":wf*idf},...]}]
    scores={"score":0,"word_list":[]}
    for word in wordList:
        if word not in index or docID not in index[word]:
            continue
        tf = len(index[word][docID])/wordCount[docID]*1000 # 一个词在文中的频率
        df = len(index[word]) # 包含这个词的文档数
        wf = 1 + cmath.log10(tf).real # 词频
        idf = cmath.log10(fileNum / df).real # 逆文档频率
        if idf<0:
            idf=0   
        scores["word_list"].append({"word":word,"tf":tf,"df":df,"wf":wf,"idf":idf,"score":wf*idf}) 
        score += wf * idf
    scores["score"]=score
    return scores

def get_tfidf_Score(index,fileNum,docID,wordList):
    score = 0
    docID = str(docID)

    for word in wordList:

        if word not in index or docID not in index[word]:
            continue
        tf = len(index[word][docID])
        df = len(index[word])
        idf = cmath.log10(fileNum / df).real
        if idf<0:
            idf=0   
        # log.info("filenum / df",fileNum / df, "df: ",df, " idf: ", idf )
        score += tf * idf
    return score
