import os
import json
import re
import time
import openai
import main
import tools
import pandas as pd
import numpy as np
import jieba
import cProfile

# try to extract key from tools.secret, if false, print
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
#     print(str(response.choices[0].message))
    return response.choices[0].message["content"]

def extract_json(text):
    # try:
    #     # 从文本中提取 JSON 列表
    #     result_match = re.search(r"<result>(.*?)</result>", text, re.DOTALL)
    #     try:
    #         return result_match.group(1)   
    #     except:
    #         print(f"解析 JSON 失败: {text}")
    #         return []             

    # except json.JSONDecodeError:
    #     print(f"解析 JSON 失败: {text}")
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
        print(f"Writing to {textName}.json")
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
    # print(f"content is {content}")

    response = get_completion_from_messages(messages=messages, temperature=0) 
    # extract the json between the first and last square brackets
    print("response", response)
    json_res = extract_json(response)
    print(json_res)
    if len(json_res)==0:
        print("No response")
        return []

    return json_res


def generate_questions(file):
    global question_num
    for filename in os.listdir(file):
        if not os.path.exists(f'{file}/questions'):
            os.makedirs(f'{file}/questions')

        if tools.getConfig("getQuestions")==False and filename.split('.')[0]+'.json' in os.listdir(f'{file}/questions'):
            print(f"Skipping {filename}")
            continue
        # if is a folder,skip it
        if os.path.isdir(f'{file}/{filename}'):
            print(f"Skipping folder {filename}")
            continue

        print(f"Generating questions for {filename}")
        textName=filename.split('.')[0]
        result={"doc ID":int(textName),"question_list":[]}
        with open(f'{file}/{filename}', 'r', encoding='utf-8') as f:
            json_data=json.load(f)
            for i, item in enumerate(json_data):
                print(f"Generating questions for {filename} {i+1}/{len(json_data)}")
                qq=query_questions(item["page_content"])
                question_num+=len(qq)
                result["question_list"].append({
                    "content" : item["page_content"],
                    "questions":qq
                })
                time.sleep(3)
            dump_question(file,textName,result)          

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
    global failure_num
    for filename in os.listdir(question_file):
        with open( f'{question_file}/{filename}' ,'r',encoding='utf-8')as f:
            # test if the corresponding content file is empty
            if os.path.getsize(f'{tools.reuterspath}/{filename.split(".")[0]}-0.json')==0:
                continue

            json_data = json.load(f)
            questions = json_data["question_list"]
            # 看看retrieve的第一条的结果是不是想要的东西
            for item in questions:
                print(f"Retrieving {filename} {item['content']}")
                for question in item["questions"]:
                    serching_res=main.searching(question["question"],searchType)
                    if searchType!=7:
                        # 形式：[[97-3,7.445],...]
                        resFull=[[tools.showDocID(x[DOC_ID]),x[SCORE],x[WORD_LIST]] for x in serching_res]
                        if len(resFull)>10:
                            resFull=resFull[:10]
                        # 形式 970003
                        res=[x[DOC_ID] for x in serching_res[:3]]
                        # 形式：97-3
                        show=[tools.showDocID(x) for x in res]
                        # 形式：97
                        mainFile=[tools.mainDocID(x) for x in res]
                        print(res)
                        if int(json_data["doc ID"]) not in mainFile:
                            fullContent={
                                "retrieved_title":[],
                                "retrieved_content":[]
                            }
                            failure_num[searchType]+=1
                            failures.append({
                                "question":question["question"],
                                "retrieved":show,
                                "expected":int(json_data["doc ID"]),
                                "method":searchType
                            })
                            # open the file in res and collect the first page_content
                            for i in show:
                                with open(f'{tools.reuterspath}/{i}.json', 'r', encoding='utf-8') as f2:
                                    content_list=json.load(f2)
                                    print(content_list)
                                    try:
                                        fullContent["retrieved_title"].append(content_list[0]["metadata"]["title"])
                                    except:
                                        fullContent["retrieved_title"].append(content_list[0]["metadata"]["source"])
                                    fullContent["retrieved_content"].append(content_list[0]["page_content"])

                            failuresFull.append({
                                "question":question["question"],
                                "expected":int(json_data["doc ID"]),
                                "retrieved":show,
                                "score":'<hr>'.join([f'doc_Id: {x[0]}, score: {x[1]:.3f}' for x in resFull]),
                                # word_list has this structure:{"word":word,"tf":tf,"df":df,"wf":wf,"idf":idf,"score":wf*idf}
                                "word_list":'<hr>'.join("<br>".join(f'{x["word"]}: score:{x["score"]:.3f} tf: {x["tf"]:.3f}, df: {x["df"]:.3f}, wf: {x["wf"]:.3f}, idf: {x["idf"]:.3f}]'for x in y[2]["word_list"]) for y in resFull),
                                "expected_content":item["content"],
                                # TODO 这里需要提供实际retrieve的内容
                                "retrieved_title":'<hr>'.join(fullContent["retrieved_title"]),
                                "retrieved_content":'<hr>'.join(fullContent["retrieved_content"]),
                                "method":searchType
                            })

    with open(f'bad_case/failure_{searchType}.json', 'w',encoding='utf-8') as f:
        json.dump(failures, f,ensure_ascii=False, indent=4)
    with open(f'bad_case/failureFull_{searchType}.json', 'w',encoding='utf-8') as f:
        json.dump(failuresFull, f,ensure_ascii=False, indent=4)
    
    # 转换为HTML
    df = pd.DataFrame(failures)
    html = df.to_html(escape=False)
    # 写入HTML文件
    with open(f'bad_case/failure_{searchType}.html', 'w',encoding='utf-8') as f:
        f.write(html)

    # 转换为HTML
    df = pd.DataFrame(failuresFull)
    html = df.to_html(escape=False)
    # 写入HTML文件
    with open(f'bad_case/failureFull_{searchType}.html', 'w',encoding='utf-8') as f:
        f.write(html)

def evaluate_accuracy():
    # for questions in questions fold, count number
    global failure_num
    global question_num
    global question_file
    failure_num=[0,0,0,0,0,0,0,0]
    question_num=0
    for filename in os.listdir(question_file):
        with open( f'{question_file}/{filename}' ,'r',encoding='utf-8')as f:
            json_data = json.load(f)
            questions = json_data["question_list"]
            question_num+=len(questions)
            # 看看retrieve的第一条的结果是不是想要的东西
    print(f"Total number of questions generated: {question_num}")
    print(f"Total number of failures: {failure_num}")
    fn=np.array(failure_num)
    fn=fn/2
    print(f"Percentage of failures: {fn.tolist()}")

def extract_failure_retrieve():
    # 打开 ./bad_case 文件夹，读取所有文件名, 取出其中 .json 文件
    bad_case_path = os.path.join(tools.projectpath, 'bad_case')
    bad_case_files = os.listdir(bad_case_path)
    bad_case_files = [file for file in bad_case_files if file.endswith('.json')]
    bad_case_files = [file for file in bad_case_files if file.startswith('failureFull')]
    print("bad_case_files:",bad_case_files)
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
                print(f'split_question {case["question"]}')
                temp={
                    "question": case["question"],
                    "split_question":list(jieba.cut(case['question'])),
                    "expected": case["expected"],
                    "retrieved": case["retrieved"],
                    "score": case["score"],
                    "word_list":case["word_list"],
                    "expected_content": case["expected_content"],
                    "retrieved_title": case["retrieved_title"],
                    "retrieved_content": case["retrieved_content"],
                    "method": case["method"],
                }
                json_data[j]=temp

            # add "in_list" key
            for j,case in enumerate(json_data):
                print(f'analyzing expacted {case["question"]}')
                # if the expected doc_id is in the "score" doc_Id, then in_list is the rank, otherwise is -1
                # change score into a dict list with key "doc_Id" and "score"
                expacted=case['expected']
                score_list= case['score'].split('<hr>')
                score_list = [score.split(', score: ') for score in score_list]
                score_list = [{'doc_Id': score[0].split(': ')[1], 'score': float(score[1])} for score in score_list]
                doc_list = [tools.mainDocID(doc['doc_Id']) for doc in score_list]

                if expacted not in doc_list:
                    temp={
                        "question": case["question"],
                        "split_question":case["split_question"],
                        "expected": case["expected"],
                        "in_list": -1,
                        "retrieved": case["retrieved"],
                        "score": case["score"],
                        "word_list":case["word_list"],
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
                            "score": case["score"],
                            "word_list":case["word_list"],
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


# 文档分为切分为每一个小文档的文档和一整个大文档
# generate_questions(f'{tools.reuterspath}\\wholeFiles')

# profiler = cProfile.Profile()
# num=1
# profiler.runctx('retrieve_files(question_file, num)', globals(), locals())

# retrieve_files(question_file,2)
extract_failure_retrieve()  
evaluate_accuracy()