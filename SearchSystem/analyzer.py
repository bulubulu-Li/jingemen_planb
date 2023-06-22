import os
import tools
import json
import jieba
import pandas as pd

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
            
            # 转换为HTML
            df = pd.DataFrame(json_data)
            html = df.to_html(escape=False)
            with open('bad_case/failureUpdate_'+index+'.html', 'w', encoding='utf-8') as f1:
                f1.write(html)

            with open('bad_case/worstCases_'+index+'_fail.json', 'w', encoding='utf-8') as f1:
                json.dump(fail_files, f1, ensure_ascii=False, indent=4)

            # 转换为HTML
            df = pd.DataFrame(fail_files)
            html = df.to_html(escape=False)
            with open('bad_case/worstCases_'+index+'_fail.html', 'w', encoding='utf-8') as f1:
                f1.write(html)

extract_failure_retrieve()        




