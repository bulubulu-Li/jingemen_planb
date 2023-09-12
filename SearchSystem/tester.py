import logging
import sys
import os

projectpath = os.path.abspath(__file__)
projectpath = projectpath[:projectpath.find('jingemen_planb') + len('jingemen_planb')]
print(f'projectpath is {projectpath}')
if sys.path.count(projectpath)==0:
    sys.path.append(projectpath)

from Log.log import log,switchToStd
# update logger to log.info to stdout
switchToStd()

import copy

import json
import re
import time
import openai
import searchSystem 
import pandas as pd
import numpy as np
import jieba
import cProfile
import SearchSystem.tools as tools
from SearchSystem.DataManager import DataForm,BaseDataManager,SqlDataManager

main=searchSystem.SearchSystem()
# try to extract key from tools.secret, if false, log.info
DOC_ID=1
SCORE=0
WORD_LIST=2
question_num=0
# 建立一个错误数组，长度为7
failure_num = [0 for i in range(7)]
question_file=tools.reuterspath+"\\questions"

def get_completion(prompt, model="gpt-3.5-turbo-0613"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_completion_from_messages(messages, model="gpt-3.5-turbo-16k-06130", temperature=0.3):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
#     log.info(str(response.choices[0].message))
    return response.choices[0].message["content"]

def extract_json(text):
    # try:
    #     # 从文本中提取 JSON 列表
    #     result_match = re.search(r"<result>(.*?)</result>", text, re.DOTALL)
    #     try:
    #         return result_match.group(1)   
    #     except:
    #         log.info(f"解析 JSON 失败: {text}")
    #         return []             

    # except json.JSONDecodeError:
    #     log.info(f"解析 JSON 失败: {text}")
    #     return []
    json_list = []
    pattern = re.compile(r'\{.*?\}', re.DOTALL)
    matches = pattern.findall(text)
    for match in matches:
        json_element = json.loads(match)
        json_list.append(json_element)
    return json_list

def json_to_html_table(json_file):
    # 读取json文件
    fileName=json_file.split("\\")[-1].split(".")[0]
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 创建一个DataFrame
    df = pd.DataFrame(data)
    # 转换为HTML
    html = df.to_html()
    # 写入HTML文件
    with open('table.html', 'w', encoding='utf-8') as f:
        f.write(html)

def dump_question(file,textName,result):
    # if questions file does not exist, create it
    if not os.path.exists(f'{file}/questions'):
        os.makedirs(f'{file}/questions')

    with open(f'{file}/questions/{textName}.json', 'w', encoding='utf-8') as f:
        log.info(f"Writing to {textName}.json")
        json.dump(result, f, ensure_ascii=False, indent=4)
        f.close()

def query_questions(content):
    # TODO deal with long content
    if len(content)>3000:
        return []
    messages =  [   
    {   
        'role': 'system',
        'content':f"""你是一个问答对生成机器人，请基于之后user给出的<article></article>中的文章，提取出文章中的问答对"""
    },
    # {   
    #     'role': 'user',
    #     'content':f"""
    #     我将依照如下步骤来解决这个问题:\n
    #     1. 判断文章中是否有问答对\n
    #     2. 如果文章中没有问答对，先执行<extra></extra>中的步骤再继续执行3，如果有，直接执行3\n
    #     3. 把问答对放入一个json格式的列表中，json放入<result></result>标签中；每个json对象有2个key:“information”代表提取的信息，“question”代表与之对应的问题，例子如下：\n
    #     <result>\n
    #     {{\n
    #         "information": "xxx",\n
    #         "question": "xxx"\n
    #     }}\n
    #     </result>\n
    #     \n
    #     我将保证问题信息的完整，不需要这篇文章存在就可以明白问题的意思\n
    #     我将保证提出的问题可以通过阅读这篇文章得到解答，不要提出需要额外知识的问题\n
    #     \n
    #     <extra>\n
    #     i. 分点提取出1-5个能从文中获得的信息。\n
    #     ii. 对每个信息，设计一个针对该信息的问题，形成问答对\n
    #     </extra>\n"""


    #     },
    {   
        'role': 'user',
        'content':
        f"""
        根据给定的问题和答案，编写一个符合以下格式的回答：

{{
"information": "<将答案部分转化为一段连贯的文字>",
"question": "<编写一个不依赖答案部分上下文即可理解的完整的疑问句> 或者 如果该疑问句依赖于特定上下文无法单独理解，返回 false"
}}

另外，对于没有明显问答的文章，提供一段精炼的信息，并提出一个能够通过阅读文章得到答案的问题。

例如：

Q:
运动损伤的一般处理方法有哪些？\n\n（1）冷疗法；（2）热疗法；（3）拔罐疗法；（4）药物疗法；（5）保护支持带。

A:
{{
"information": "运动损伤的处理方法有冷疗法、热疗法、拔罐疗法、药物疗法、保护支持带",
"question": "一般来说，我们可以采用哪些方法来处理运动损伤？"
}}

另一个例子：

Q:
"中心城区房地产开发项目的车位车库\n从9月1日起，达到条件可以租售。\n但到底哪些可租哪些可售？\n租售要具备什么条件？\n买到手的车位是否可以随意转手？\n……\n诸多问题困扰着开发企业，\n也困扰着居民区的有车一族。\n昨日，\n市住建部门下发《通知》——\n今年8月中旬，我市下发《关于规范中心城区房地产开发项目地下车位管理的通知》，明确规定，从9月1日起，地下停车场建设用地使用权办理不动产登记后，可以依法转让、出租、抵押。然而，由于交易细则不明确，让实际交易存在很多困难。\n今日，市住房和城乡建设局下发《关于规范中心城区房地产开发项目车位车库交易管理工作的通知》（以下简称《通知》），对很多交易细则进行了具体明确。\n《通知》要求，中心城区范围内房地产开发项目建筑区划内，规划用于停放汽车的车位、车库交易都必须按《通知》执行。同时，要求房地产开发企业严格执行《通知》规定，规范停车位租售行为，合理确定价格，不得滥用市场支配权，变相抬高、垄断、操控停车位价格，不得扰乱房地产市场健康发展秩序。"

A:
{{
"information": "根据市住房和城乡建设局下发的《通知》, 中心城区范围内的房地产开发项目，规划用于停放汽车的车位、车库交易必须按《通知》执行。《通知》要求房地产开发企业严格执行规定，规范停车位租售行为，合理确定价格，不得滥用市场支配权，变相抬高、垄断、操控停车位价格，不得扰乱房地产市场健康发展秩序。",
"question": "房地产开发商租售停车位有限制吗？"
}}
?"
}}
"""


        },
        {

        'role':'user', 
        'content':f"""   
        下面是文章：\n
        <article>\n
        {content}
        </article>"""
        },
    ]
    # log.info(f"content is {content}")

    response = get_completion_from_messages(messages=messages, temperature=0) 
    # extract the json between the first and last square brackets
    log.info("response", response)
    json_res = extract_json(response)
    log.info(json_res)
    if len(json_res)==0:
        log.info("No response")
        return []

    return json_res


def generate_questions(file):
    global question_num
    for filename in os.listdir(file):
        if not os.path.exists(f'{file}/questions'):
            os.makedirs(f'{file}/questions')

        if tools.getConfig("getQuestions")==False and filename.split('.')[0]+'.json' in os.listdir(f'{file}/questions'):
            log.info(f"Skipping {filename}")
            continue
        # if is a folder,skip it
        if os.path.isdir(f'{file}/{filename}'):
            log.info(f"Skipping folder {filename}")
            continue

        log.info(f"Generating questions for {filename}")
        textName=filename.split('.')[0]
        result={"doc ID":int(textName),"question_list":[]}
        with open(f'{file}/{filename}', 'r', encoding='utf-8') as f:
            json_data=json.load(f)
            for i, item in enumerate(json_data):
                log.info(f"Generating questions for {filename} {i+1}/{len(json_data)}")
                qq=query_questions(item["page_content"])
                question_num+=len(qq)
                result["question_list"].append({
                    "content" : item["page_content"],
                    "questions":qq
                })
                time.sleep(3)
            dump_question(file,textName,result)          

def update_questions():
    # for questions items in questions folde
    json_data=""
    mainID=""
    for questionListFile in os.listdir(f'{tools.reuterspath}/questions'):
        with open(f'{tools.reuterspath}/questions/{questionListFile}', 'r', encoding='utf-8') as f:
            json_data=json.load(f)
            mainID=json_data["doc ID"]
            for i, item in enumerate(json_data["question_list"]):
                # add a more precision doc ID to each question, by check if the pagecontent equel to 
                for filename in os.listdir(tools.reuterspath):
                    # skip folder
                    if os.path.isdir(f'{tools.reuterspath}/{filename}'):
                        continue
                    # skip empty file
                    if os.path.getsize(f'{tools.reuterspath}/{filename}')==0:
                        continue
                    log.info(f"deal with {filename}")
                    if filename.split('-')[0]==str(mainID):
                        with open(f'{tools.reuterspath}/{filename}', 'r', encoding='utf-8') as f2:
                            json_data2=json.load(f2)
                            if json_data2[0]["page_content"]==item["content"]:
                                json_data["question_list"][i]["doc ID"]=filename.split('.')[0]
                                break
        dump_question(tools.reuterspath,mainID,json_data)

'''
    the structure of a question file is like this:
    {
        "doc ID": "doc ID",
        "question_list": [
            {
                "content": "content",
                "questions": [
                    {
                        "information": "information",   
                        "question": "question"
                    },
                    ...
                ]
            },
            ...
        ]
    }  
'''
def retrieve_files(question_file,searchType):
    failures =[]
    failuresFull=[]
    worstCases=[]
    global failure_num
    files=SqlDataManager()
    for dataItem in files:
        questions = dataItem.questions
        # 看看retrieve的第一条的结果是不是想要的东西
        log.info(f"Retrieving {dataItem.docId} Method {searchType}")
        for ques in questions:
            searching_res,expectList=main.search(ques,searchType,expectList=[dataItem.docId_qa,dataItem.docId_qq])
            if searchType!=88:
                # 形式：[[97-3,7.445],...]
                resFull=[[x[DOC_ID],x[SCORE],x[WORD_LIST]] for x in searching_res]
                if len(resFull)>10:
                    resFull=resFull[:10]
                # 形式 10097
                res=[x[DOC_ID] for x in searching_res[:10]]
                # 形式：97
                mainFile_temp=[dataItem.docIdManager.get_docId(x) for x in res]
                mainFile=[]
                # delete same elements in mainFile
                for i in mainFile_temp:
                    if i not in mainFile:
                        mainFile.append(i)
                # log.info(res)
                if dataItem.docId not in mainFile[:3]:
                    fullContent={
                        "retrieved_title":[],
                        "retrieved_content":[]
                    }
                    failure_num[searchType]+=1
                    failures.append({
                        "question":ques,
                        "retrieved":mainFile_temp,
                        "expected":dataItem.docId,
                        "method":searchType
                    })
                    # open the file in res and collect the first page_content
                    for i in res:
                        fullContent["retrieved_title"].append(files[i].title)
                        fullContent["retrieved_content"].append(files[i].page_content)
                    
                    word_detail=[]
                    for y in resFull:
                        word_temp=[]
                        for i in y[2]["word_list"]:
                            word_temp.append({
                                "word":i["word"],
                                "score":f'{i["score"]:.3f}',
                                "tf":f'{i["tf"]:.3f}',
                                "df":f'{i["df"]:.3f}',
                                "wf":f'{i["wf"]:.3f}',
                                "idf":f'{i["idf"]:.3f}'
                            })
                        word_detail.append(word_temp)
                    
                    expect_word_detail=[]
                    for y in expectList:
                        word_temp=[]
                        for i in y[2]["word_list"]:
                            word_temp.append({
                                "word":i["word"],
                                "score":f'{i["score"]:.3f}',
                                "tf":f'{i["tf"]:.3f}',
                                "df":f'{i["df"]:.3f}',
                                "wf":f'{i["wf"]:.3f}',
                                "idf":f'{i["idf"]:.3f}'
                            })
                        expect_word_detail.append(word_temp)
                    log.info(f'expection: {expectList}')
                    expect_detail={
                        "retrieve_method":[files.get_method(x[1]) for x in expectList],
                        "doc_score":[f'{x[0]:.3f}' for x in expectList],
                        "rank":[int(x[3]) for x in expectList],
                        "word_detail":copy.deepcopy(expect_word_detail),
                    }

                    score_detail={
                        "retrieve_method":[files.get_method(x[0]) for x in resFull],
                        "retrieved":copy.deepcopy(mainFile_temp),
                        "doc_score":[f'{x[1]:.3f}' for x in resFull],
                        "retrieved_title":copy.deepcopy(fullContent["retrieved_title"]),
                        "word_detail":copy.deepcopy(word_detail),
                        "retrieved_content":copy.deepcopy(fullContent["retrieved_content"])
                    }
                    try:
                        temp={
                            "question":ques,
                            "split_question":list(jieba.cut(ques)),
                            "expected":dataItem.docId,
                            "expected_detail":copy.deepcopy(expect_detail),
                            "in_list":int(mainFile.index(dataItem.docId)),
                            "expected_title":dataItem.title,
                            "expected_content":dataItem.page_content,
                            "score_detail":copy.deepcopy(score_detail),
                            "method":searchType
                        }
                        failuresFull.append(temp)
                    except:
                        temp={
                            "question":ques,
                            "split_question":list(jieba.cut(ques)),
                            "expected":dataItem.docId,
                            "expected_detail":copy.deepcopy(expect_detail),
                            "in_list":-99,
                            "expected_title":dataItem.title,
                            "expected_content":dataItem.page_content,
                            "score_detail":copy.deepcopy(score_detail),
                            "method":searchType
                        }
                        failuresFull.append(temp)
                        # 删除temp的in_list 这个key
                        del temp["in_list"]
                        worstCases.append(temp)



    with open(f'bad_case/failure_{searchType}.json', 'w',encoding='utf-8') as f:
        json.dump(failures, f,ensure_ascii=False, indent=4)
    with open(f'bad_case/failureFull_{searchType}.json', 'w',encoding='utf-8') as f:
        json.dump(failuresFull, f,ensure_ascii=False, indent=4)
    with open(f'bad_case/worstCases_{searchType}.json', 'w',encoding='utf-8') as f:
        json.dump(worstCases, f,ensure_ascii=False, indent=4)
    
    # 转换为HTML
    html = to_html(failures)
    # 写入HTML文件
    with open(f'bad_case/failure_{searchType}.html', 'w',encoding='utf-8') as f:
        f.write(html)

    # 转换为HTML
    html = to_html(failuresFull)
    # 写入HTML文件
    with open(f'bad_case/failureFull_{searchType}.html', 'w',encoding='utf-8') as f:
        f.write(html)

    # 转换为HTML
    html = to_html(worstCases)
    # 写入HTML文件
    with open(f'bad_case/worstCases_{searchType}.html', 'w',encoding='utf-8') as f:
        f.write(html)

def retrieve_files_update(question_file,searchType):

    failures =[]
    failuresFull=[]
    worstCases=[]
    global failure_num
    fi=SqlDataManager()
    files=[]
    # 从question_file中读取所有的问题
    with open(question_file,'r',encoding='utf-8') as f:
        qs=json.load(f)
    for i, dataItem in enumerate(fi):
        # 检查这个项目有没有对应的生成的问题，如果有在item中添加这个问题
        files.append(dataItem)
        for item in qs:
            print(f'item is {item["question"]} dataItem is {dataItem.title}')
            if dataItem.title==item["question"]:
                files[i].questions.append(item["generate"])
                print('got')
                print(files[i].questions)

    print("after append")

    for dataItem in files:
        questions = dataItem.questions
        if len(questions)==0:
            print(f"Skipping {dataItem.docId}")
            continue
        # 看看retrieve的第一条的结果是不是想要的东西
        log.info(f"Retrieving {dataItem.docId} Method {searchType}")
        for ques in questions:
            searching_res,expectList=main.search(ques,searchType,expectList=[dataItem.docId_qa,dataItem.docId_qq])
            if searchType!=88:
                # 形式：[[97-3,7.445],...]
                resFull=[[x[DOC_ID],x[SCORE],x[WORD_LIST],x[3]] for x in searching_res]
                if len(resFull)>10:
                    resFull=resFull[:10]
                print(f'resFull is {resFull}')
                # 形式 10097
                res=[x[DOC_ID] for x in searching_res[:10]]
                # 形式：97
                mainFile_temp=[dataItem.docIdManager.get_docId(x) for x in res]
                mainFile=[]
                # delete same elements in mainFile
                for i in mainFile_temp:
                    if i not in mainFile:
                        mainFile.append(i)
                # log.info(res)
                # if dataItem.docId not in mainFile[:3]:
                if True:
                    fullContent={
                        "retrieved_title":[],
                        "retrieved_content":[]
                    }
                    failure_num[searchType]+=1
                    failures.append({
                        "question":ques,
                        "retrieved":mainFile_temp,
                        "expected":dataItem.docId,
                        "method":searchType
                    })
                    # open the file in res and collect the first page_content
                    for i in res:
                        fullContent["retrieved_title"].append(fi[i].title)
                        fullContent["retrieved_content"].append(fi[i].page_content)
                    
                    print(f'fullContent is {fullContent}')

                    word_detail=[]
                    for y in resFull:
                        word_temp=[]
                        for i in y[2]["word_list"]:
                            word_temp.append({
                                "word":i["word"],
                                "score":f'{i["score"]:.3f}',
                                "tf":f'{i["tf"]:.3f}',
                                "df":f'{i["df"]:.3f}',
                                "wf":f'{i["wf"]:.3f}',
                                "idf":f'{i["idf"]:.3f}'
                            })
                        word_detail.append(word_temp)
                    
                    expect_word_detail=[]
                    for y in expectList:
                        word_temp=[]
                        for i in y[2]["word_list"]:
                            word_temp.append({
                                "word":i["word"],
                                "score":f'{i["score"]:.3f}',
                                "tf":f'{i["tf"]:.3f}',
                                "df":f'{i["df"]:.3f}',
                                "wf":f'{i["wf"]:.3f}',
                                "idf":f'{i["idf"]:.3f}'
                            })
                        expect_word_detail.append(word_temp)
                    log.info(f'expection: {expectList}')
                    expect_detail={
                        "retrieve_method":[fi.get_method(x[1]) for x in expectList],
                        "doc_score":[f'{x[0]:.3f}' for x in expectList],
                        "rank":[int(x[3]) for x in expectList],
                        "word_detail":copy.deepcopy(expect_word_detail),
                    }

                    score_detail={
                        "retrieve_method":[fi.get_method(x[0]) for x in resFull],
                        "retrieved":copy.deepcopy(mainFile_temp),
                        "doc_score":[f'{x[1]:.3f}' for x in resFull],
                        "jaccard":[f'{x[3]["jaccard"]:.3f}' for x in resFull],
                        "cqrctr":[f'{x[3]["cqrctr"]:.3f}' for x in resFull],
                        "left":[f'{x[3]["left"]:.3f}' for x in resFull],
                        "retrieved_title":copy.deepcopy(fullContent["retrieved_title"]),
                        "word_detail":copy.deepcopy(word_detail),
                        "retrieved_content":copy.deepcopy(fullContent["retrieved_content"]),
                    }
                    try:
                        temp={
                            "question":ques,
                            "split_question":list(jieba.cut(ques)),
                            "expected":dataItem.docId,
                            "expected_detail":copy.deepcopy(expect_detail),
                            "in_list":int(mainFile.index(dataItem.docId)),
                            "expected_title":dataItem.title,
                            "expected_content":dataItem.page_content,
                            "score_detail":copy.deepcopy(score_detail),
                            "method":searchType
                        }
                        failuresFull.append(temp)
                    except:
                        temp={
                            "question":ques,
                            "split_question":list(jieba.cut(ques)),
                            "expected":dataItem.docId,
                            "expected_detail":copy.deepcopy(expect_detail),
                            "in_list":-99,
                            "expected_title":dataItem.title,
                            "expected_content":dataItem.page_content,
                            "score_detail":copy.deepcopy(score_detail),
                            "method":searchType
                        }
                        failuresFull.append(temp)
                        # 删除temp的in_list 这个key
                        del temp["in_list"]
                        worstCases.append(temp)

    with open(f'bad_case/failure_{searchType}.json', 'w',encoding='utf-8') as f:
        json.dump(failures, f,ensure_ascii=False, indent=4)
    with open(f'bad_case/failureFull_{searchType}.json', 'w',encoding='utf-8') as f:
        json.dump(failuresFull, f,ensure_ascii=False, indent=4)
    with open(f'bad_case/worstCases_{searchType}.json', 'w',encoding='utf-8') as f:
        json.dump(worstCases, f,ensure_ascii=False, indent=4)
    
    # 转换为HTML
    html = to_html(failures)
    # 写入HTML文件
    with open(f'bad_case/failure_{searchType}.html', 'w',encoding='utf-8') as f:
        f.write(html)

    # 转换为HTML
    html = to_html(failuresFull)
    # 写入HTML文件
    with open(f'bad_case/failureFull_{searchType}.html', 'w',encoding='utf-8') as f:
        f.write(html)

    # 转换为HTML
    html = to_html(worstCases)
    # 写入HTML文件
    with open(f'bad_case/worstCases_{searchType}.html', 'w',encoding='utf-8') as f:
        f.write(html)




# 目的是处理score_detail and the word_list with in it
def to_html(json_data_input):
    # copy json_date_input to json_data
    json_data=copy.deepcopy(json_data_input)
    for j,item in enumerate(json_data):
        # if item don't have key score_detail,break
        if "score_detail" not in item:
            break
        for i,v in enumerate(item["score_detail"]["word_detail"]):
            item["score_detail"]["word_detail"][i]=pd.DataFrame(v).to_html(escape=False).replace('\n','')
        for i,v in enumerate(item["expected_detail"]["word_detail"]):
            item["expected_detail"]["word_detail"][i]=pd.DataFrame(v).to_html(escape=False).replace('\n','')
        item["score_detail"]=pd.DataFrame(item["score_detail"]).to_html(escape=False).replace('\n','')
        item["expected_detail"]=pd.DataFrame(item["expected_detail"]).to_html(escape=False).replace('\n','')
        json_data[j]=item
        # log.info("item is ",item["score_detail"])
    return pd.DataFrame(json_data).to_html(escape=False)

# def to_xlsx(json_data):
    
    
def evaluate_accuracy():
    # for questions in questions fold, count number
    global failure_num
    global question_num
    global question_file
    failure_num=[0,0,0,0,0,0,0,0]
    worst_num=[0,0,0,0,0,0,0,0]
    question_num=BaseDataManager().len

    # get file in bad_case
    bad_case_path = os.path.join(tools.searchsystempath, 'bad_case')
    full_cases=[x for x in os.listdir(bad_case_path) if x.endswith('.json') and x.startswith('failureFull')]
    worst_cases=[x for x in os.listdir(bad_case_path) if x.endswith('.json') and x.startswith('worstCases')]
    # calculate item numbers in full or worst cases file, by loading to json and count the lenth of list
    for file in full_cases:
        method=int(file.split('_')[1].split('.')[0])
        with open(f'bad_case/{file}','r',encoding='utf-8') as f:
            json_data=json.load(f)
            failure_num[method]+=len(json_data)
    for file in worst_cases:
        method=int(file.split('_')[1].split('.')[0])
        with open(f'bad_case/{file}','r',encoding='utf-8') as f:
            json_data=json.load(f)
            worst_num[method]+=len(json_data)
    log.info(f"Total number of questions generated: {question_num}")
    log.info(f"Total number of failures: {failure_num}")
    log.info(f"Total number of worst   : {worst_num}")
    fn=np.array(failure_num)
    fn=1-fn/question_num
    wn=np.array(worst_num)
    wn=1-wn/question_num
    log.info(f"Percentage of failures: {[f'{x*100:.1f}%' for x in fn.tolist()]}")
    log.info(f"Percentage of worst   : {[f'{x*100:.1f}%' for x in wn.tolist()]}")

def extract_failure_retrieve():
    # 打开 ./bad_case 文件夹，读取所有文件名, 取出其中 .json 文件
    bad_case_path = os.path.join(tools.searchsystempath, 'bad_case')
    bad_case_files = os.listdir(bad_case_path)
    bad_case_files = [file for file in bad_case_files if file.endswith('.json')]
    bad_case_files = [file for file in bad_case_files if file.startswith('failureFull')]
    log.info("bad_case_files:",bad_case_files)
    # case example:
    # {
    #     "question": "哪些人容易患上钩体病？",
    #     "expected": 102,
    #     "retrieved": [
    #         "127-11",
    #         "316-1",
    #         "317-5"
    #     ],
    #     "score": "doc_Id: 127-11, score: 8.8460<hr>doc_Id: 316-1, score: 7.6597<hr>doc_Id: 317-5, score: 6.8823<hr>doc_Id: 125-11, score: 6.8823<hr>doc_Id: 103-18, score: 6.8823<hr>doc_Id: 71-13, score: 6.8823<hr>doc_Id: 133-17, score: 6.2878<hr>doc_Id: 116-15, score: 6.2800<hr>doc_Id: 111-11, score: 6.2800<hr>doc_Id: 310-13, score: 6.0673",
    #     "expected_content": "钩体病易感人群\n\n多发生于夏秋汛期的抗洪救灾和在田间作业的人员。",
    #     "retrieved_title": "json/new_json_188.json<hr>json/new_json_84.json<hr>json/new_json_85.json",
    #     "retrieved_content": "什么是钩体病？\n\n钩端螺旋体病（简称钩体病）是由致病性钩端螺旋体引起的人兽共患病。<hr>钩体病的诊断\n\n钩体病的诊断主要依靠流行病学资料、临床表现和实验室检查。从患者血液或尿液或脑脊液分离或检测到钩端螺旋体能明确诊断；检测病人恢复期血清抗体比急性期血清的钩端螺旋体抗体效价增高4倍或4倍以上，也能诊断为钩体病患者。<hr>钩体病流行期措施\n\n在钩体病流行的疫点，对病人和钩体污染环境进行管理。对病人及时治疗，在疫点对传染源进行带菌率调查，如猪带菌率、鼠密度和鼠带菌率调查并采取相应的措施。对流行的菌型进行鉴定，以便采取针对性预防和治疗措施。",
    #     "method": 1
    # },
    for file in bad_case_files:
        fail_files=[]
        # open and read the file using utf-8
        file_path = os.path.join(bad_case_path, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            # read json from file
            json_data = json.load(f)
            # add a key "in_list" to the json, with int value

            # add "split_question" key
            for j,case in enumerate(json_data):
                log.info(f'split_question {case["question"]}')
                temp={
                    "question": case["question"],
                    "split_question":list(jieba.cut(case['question'])),
                    "expected": case["expected"],
                    "retrieved": case["retrieved"],
                    # "score": case["score"],
                    "score_detail":case["score_detail"],
                    "expected_content": case["expected_content"],
                    "retrieved_title": case["retrieved_title"],
                    "retrieved_content": case["retrieved_content"],
                    "method": case["method"],
                }
                json_data[j]=temp

            # add "in_list" key
            for j,case in enumerate(json_data):
                log.info(f'analyzing expacted {case["question"]}')
                # if the expected doc_id is in the "score" doc_Id, then in_list is the rank, otherwise is -1
                # change score into a dict list with key "doc_Id" and "score"
                expacted=case['expected']
                score_list= case['score_detail'].split('<hr>')
                log.info("score_list")
                log.info(score_list)
                score_list = [score.split('<br>')[0] for score in score_list]
                log.info("score_list #")
                log.info(score_list)
                score_list = [score.split(', doc_score: ') for score in score_list]
                log.info("score_list , doc_score: ")
                log.info(score_list)
                score_list = [{'doc_Id': score[0].split(': ')[1], 'score': float(score[1])} for score in score_list]
                doc_list = [BaseDataManager().get_method(doc['doc_Id']) for doc in score_list]

                if expacted not in doc_list:
                    temp={
                        "question": case["question"],
                        "split_question":case["split_question"],
                        "expected": case["expected"],
                        "in_list": -1,
                        "retrieved": case["retrieved"],
                        # "score": case["score"],
                        "score_detail":case["score_detail"],
                        "expected_content": case["expected_content"],
                        "retrieved_title": case["retrieved_title"],
                        "retrieved_content": case["retrieved_content"],
                        "method": case["method"],
                    }
                    json_data[j]=temp
                    fail_files.append(case)
                    continue

                for i,docId in enumerate(doc_list):
                    if expacted==docId:
                        temp={
                            "question": case["question"],
                            "split_question":case["split_question"],
                            "expected": case["expected"],
                            "in_list": i,
                            "retrieved": case["retrieved"],
                            # "score": case["score"],
                            "score_detail":case["score_detail"],
                            "expected_content": case["expected_content"],
                            "retrieved_title": case["retrieved_title"],
                            "retrieved_content": case["retrieved_content"],
                            "method": case["method"],
                        }
                        json_data[j]=temp
                        break
                
            # extract failure index
            index=file.split('.')[0].split('_')[1]
            # write the json into file
            with open('bad_case/failureUpdate_'+index+'.json', 'w', encoding='utf-8') as f1:
                json.dump(json_data, f1, ensure_ascii=False, indent=4)
            
            # 转换为HTML和csv
            df = pd.DataFrame(json_data)
            html = df.to_html(escape=False)
            with open('bad_case/failureUpdate_'+index+'.html', 'w', encoding='utf-8') as f1:
                f1.write(html)
            df = pd.json_normalize(json_data)
            df.to_csv('bad_case/failureUpdate_'+index+'.csv', encoding='utf-8-sig')

            with open('bad_case/worstCases_'+index+'_fail.json', 'w', encoding='utf-8') as f1:
                json.dump(fail_files, f1, ensure_ascii=False, indent=4)

            # 转换为HTML和csv
            df = pd.DataFrame(fail_files)
            html = df.to_html(escape=False)
            with open('bad_case/worstCases_'+index+'_fail.html', 'w', encoding='utf-8') as f1:
                f1.write(html)
            df = pd.json_normalize(fail_files)
            df.to_csv('bad_case/worstCases_'+index+'.csv', encoding='utf-8-sig')


if __name__ == "__main__":
    # 文档分为切分为每一个小文档的文档和一整个大文档
    # generate_questions(f'{tools.reuterspath}\\wholeFiles')

    # profiler = cProfile.Profile()
    # num=1
    # profiler.runctx('retrieve_files(question_file, num)', globals(), locals())


    

    # retrieve_files(question_file,2)
    # retrieve_files(question_file,3)
    # retrieve_files(question_file,4)
    # # extract_failure_retrieve()  
    # evaluate_accuracy()

    # update_questions()

    question_file='questions.json'
    retrieve_files_update(question_file,1)
    print("finished")
    pass