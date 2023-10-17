# coding=utf-8
# Filename:    TestClassHandler.py
# Author:      ZENGGUANRONG
# Date:        2023-09-10
# description: TestClass的Tornado Handler

import json

from tornado.escape import json_decode
import tornado.ioloop
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
from tornado.options import options, define
from Log.log import log
from SearchSystem.searchSystem import SearchSystem 


class QuestionAnswerHandler(RequestHandler):
    
    def initialize(self, searching:SearchSystem):
        log.info(f'QuestionAnswerHandler initialize')   
        self.searching = searching

    async def post(self):
        request=self.request.body
        request=json_decode(request)
        log.info(f'QuestionAnswerHandler post: question:{request["question"]},isGenerate:{request["isGenerate"]}')
        sources={
            101:"用户上传",
            102:"通话生成",
            103:"知识文件",#有id
            104:"历史工单" #有id
        }
        searching=self.searching
        if request["isGenerate"] == 0:
            log.info(f'not generate {request["question"]}')
            qaList = []
            search_res = searching.searchResults(request["question"])
            if len(search_res) == 0:
                log.info(f'没有找到答案')
                response = {
                    "errCode": 2,
                    "errMsg": "can't find answer",
                    "results": None
                }
                self.write(response)
                return
            
            for item in search_res:
                # 判断sourceunit，基于item.metadata["from"]的值，判断来源
                fileLink = ""
                if  item.metadata["from"] in [103, 104] and "fromId" in item.metadata:
                    fileLink = item.metadata["fromId"]
                qaList.append(
                    {
                        "question": item.title,
                        "answer": item.page_content,
                        "source": sources[item.metadata["from"]],
                        "questionAnswerId": str(item.docId),
                        "sourceUnit": "",
                        "knowledgeFileSource": [{
                            "fileName": item.title,
                            "fileLink": fileLink
                        }]
                    }
                )
            log.info(f'questions:{[x["question"] for x in qaList]},answers:{[x["answer"] for x in qaList]}')
            response = {
                "errCode": 0,
                "errMsg": "SUCCESS",
                "results": {
                    "questionAnswerPairs": qaList
                }
            }
            log.info(f"writing {response}")
            self.write(response)
            return
        
        elif request["isGenerate"] == 1:
            log.info(f'generate {request["question"]}')
            qaPair = []
            search_res = []
            answer, search_res, fragment = searching.searchResults(request["question"], choice=7)
            answer = answer.split("参考文献")[0]
            for i, item in enumerate(search_res):
                fileLink = ""
                if  item.metadata["from"] in [103, 104] and "fromId" in item.metadata:
                    fileLink = item.metadata["fromId"]
                qaPair.append(
                    {
                        "fileName": item.title,
                        "fileLink": fileLink
                    }
                )

            response = {
                "errCode": 0,
                "errMsg": "SUCCESS",
                "results": {
                    "generateAnswers": {
                        "answer": answer,
                        "knowledgeFileSource": qaPair
                    }
                }
            }
            log.info(f"writing {response}")
            self.write(response)
            return

        else:
            log.info(f'isGenerate参数错误,需要为0或者1')
            response = {
                "errCode": 1,
                "errMsg": "isGenerate param error, need to be 0 or 1",
                "results": None
            }
            log.info(f"writing {response}")
            self.write(response)
            return

class BlockHandler(RequestHandler):
    def initialize(self, searching:SearchSystem):
        log.info(f'BlockHandler initialize')
        self.searching = searching

    async def post(self):
        addList=json_decode(self.request.body)["addList"]
        log.info(f"BlockList add: {addList}")
        self.searching.block(addList)
        self.write({"errCode":0,"errMsg":"SUCCESS","results":len(addList)})



def StartHandler(request_config: dict,handler, searching: SearchSystem):
    # 启动TestClass服务的进程
    # 注：如果是同端口，只是不同的url路径，则直接都放在handler_routes里面即可
    # 注：test_class需要在外面初始化后再传进来，而不能在initialize里面加载，initialize是每次请求都会执行一遍，例如知识问答的索引更新，肯定不能在这里面修改
    handler_routes = [(request_config["url_suffix"], handler, {"searching":searching})]
    app = Application(handlers=handler_routes)
    http_server = HTTPServer(app)
    http_server.listen(request_config["port"])
    tornado.ioloop.IOLoop.current().start()