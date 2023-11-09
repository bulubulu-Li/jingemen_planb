# coding=utf-8
# Filename:    test_class_client.py
# Author:      ZENGGUANRONG
# Date:        2023-09-10
# description: 测试用的客户端

import numpy as np
import json,requests,time,random
from multiprocessing import Pool,set_start_method

def run_client(query):
    response = requests.post("http://127.0.0.1:9090/a", json.dumps({"query": query}))
    return json.loads(response.text)

def cal_time_result(time_list):
    tp = np.percentile(time_list, [50, 90, 95, 99])
    print("tp50:{:.4f}ms, tp90:{:.4f}ms,tp95:{:.4f}ms,tp99:{:.4f}ms".format(tp[0] * 1000, tp[1]* 1000, tp[2]* 1000, tp[3]* 1000))
    print("average: {}".format(sum(time_list) / len(time_list)))
    print("qps:{:.4f}".format(len(time_list) / sum(time_list)))

def single_test(query_list, num, process_id = 0,isGenerate=0):
    # query_list:待请求query列表，num请求个数
    print("running process: process-{}".format(process_id))
    time_list = []
    for i in range(num):
        start_time = time.time()
        query = random.choice(query_list)
        requests.post("http://localhost:9091/qabot/question-answer", json.dumps({"question": query,"isGenerate":isGenerate}))
        end_time = time.time()
        time_list.append(end_time-start_time)
    return time_list


def batch_test(query_list, process_num, request_num,isGenerate=0):
    # query_list:待请求query列表，process_num进程个数，request_num请求个数(每个进程)
    pool = Pool(processes=process_num)
    process_result = []
    for i in range(process_num):
        process_result.append(pool.apply_async(single_test, args=(query_list, request_num, str(i), isGenerate)))
        # processes.append(Process(target=single_test, args=(query_list, request_num, str(i), )))
    
    pool.close()
    pool.join()

    time_list = []
    for result in process_result:
        time_list.extend(result.get())
    return time_list   


# response = requests.post("http://127.0.0.1:9090/a", json.dumps({"query": "你好啊1"}))
# print(json.loads(response.text))

# response = requests.post("http://127.0.0.1:9091/b", json.dumps({"query": "你好啊2"}))
# print(json.loads(response.text))

if __name__ == "__main__":
    time_list = [0]
    set_start_method('spawn')
    # print(run_client("你好啊")) # 单元测试
    print("===================================== 查询模式 =====================================")
    time_list = single_test(["如何提取住房公积金？","出租车计价标准","农民专业合作社年度报告内容"], 100) # 批量单进程测试
    cal_time_result(time_list=time_list)
    print("===================================== 生成模式 =====================================")
    time_list = single_test(["如何提取住房公积金？","出租车计价标准","农民专业合作社年度报告内容"], 10,isGenerate=1) # 批量单进程测试
    cal_time_result(time_list=time_list)
    print("===================================== 多进程测试 查询模式 =====================================")
    time_list = batch_test(["如何提取住房公积金？","出租车计价标准","农民专业合作社年度报告内容"], 4, 100) # 多进程压测
    cal_time_result(time_list=time_list)
    print("===================================== 多进程测试 生成模式 =====================================")
    time_list = batch_test(["如何提取住房公积金？","出租车计价标准","农民专业合作社年度报告内容"], 4, 10,isGenerate=1) # 多进程压测
    cal_time_result(time_list=time_list)