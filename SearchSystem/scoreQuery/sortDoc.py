from SearchSystem.scoreQuery import getScore
# import SearchSystem.tools as tools

DOC_ID=1

def getScoreDocList(index,fileNum, words,docList,wordCount):
    scoreDocList = []
    for doc in docList:
        scores = getScore.get_wfidf_Score(index,fileNum,doc,words,wordCount)
        score=scores["score"]
        #scoreDocList 是score和doc的list
        scoreDocList.append([score,doc,scores])
    #print(scoreDocList)
    return scoreDocList

#从大到小得到sortedDocList
def sortScoreDocList(index,fileNum,words,docList,wordCount):
    scoreDocList = getScoreDocList(index,fileNum,words,docList,wordCount)
    return sorted(scoreDocList,reverse = True)

#堆排序实现的top K查询
def TopKScore(K,index,fileNum,words,docList,wordCount):
    scoreDocList = getScoreDocList(index, fileNum, words, docList,wordCount)
    # print(scoreDocList)
    N = len(scoreDocList)
    if N is 0:
        return []
    # scoreDocList = heapsort(scoreDocList,N,2*K)
    # print("scoreDocList:",scoreDocList[0])
    # # exit()
    # L = 2*K
    # if N < 2*K: L = N
    # temp= [scoreDocList[N - x - 1] for x in range(0,L)]
    # res=[]
    # for i in range(len(temp)):
    #     if i==0:
    #         res.append(temp[i])
    #         continue
    #     if temp[i][DOC_ID]!=temp[i-1][DOC_ID]:
    #         res.append(temp[i])
    #     else:
    #         res[-1][1]=tools.setRetrieveMethod(res[-1][1],"qa + qq")
    # res=res[:K]
    # return res


    # scoreDocList元素例子：
    # [
    # 7.570853442210866,
    # 1860004,
    # {'score': 7.570853442210866, 'word_list': [
    #         {'word': '方法', 'tf': 33.333333333333336, 'df': 313, 'wf': 2.5228787452803374, 'idf': 1.2908521238258557, 'score': 3.2566633865002337
    #         },
    #         {'word': '哪些', 'tf': 6.666666666666667, 'df': 1890, 'wf': 1.8239087409443187, 'idf': 0.5099346571990601, 'score': 0.9300742785758104
    #         },
    #         {'word': '运动', 'tf': 13.333333333333334, 'df': 133, 'wf': 2.1249387366083, 'idf': 1.6625448204052184, 'score': 3.5328058902265376
    #         },
    #         {'word': '，', 'tf': 46.66666666666667, 'df': 5941, 'wf': 2.6690067809585756, 'idf': 0.012536908995617276, 'score': 0.033461095121563075
    #         },
    #         {'word': '？', 'tf': 6.666666666666667, 'df': 7696, 'wf': 1.8239087409443187, 'idf': -0.09986859765745225, 'score': -0.18215120821327846
    #         }
    #     ]
    # }
    # ]

    
    scoreDocList = heapsort(scoreDocList,N,K)
    L = K
    if N < K: L = N
    return [scoreDocList[N - x - 1] for x in range(0,L)]


def leftChild(i):
    return 2 * i + 1

def percDown(A,i,N):
    tmp = A[i]
    while leftChild(i) < N:
        child = leftChild(i)
        if child != N - 1 and A[child+1][0] > A[child][0]:
            child += 1
        if tmp[0] < A[child][0]:
            A[i] = A[child]
        else:
            break
        i = child
    A[i] = tmp
    return A

def heapsort(A,N,K):
    i = int(N / 2)
    while i >= 0:
        A = percDown(A,i,N)
        i -= 1
    i = N - 1
    end = 0
    if N - 1 > K:
        end = N - 1 - K
    while i > end:
       tem = A[0]
       A[0] = A[i]
       A[i] = tem
       percDown(A,0,i)
       i -= 1
    return A