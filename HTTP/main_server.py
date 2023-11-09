import tornado.ioloop
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
from tornado.options import options, define
import multiprocessing 

# Import the project into python path
import sys
import os

# 获取当前路径，取出'jingemen_planb'和其前部为项目路径
projectpath = os.path.abspath(__file__)
projectpath = projectpath[:projectpath.find('jingemen_planb') + len('jingemen_planb')]
print(f'projectpath is {projectpath}')
sys.path.append(projectpath)

from Log.log import log

from SearchSystem.searchSystem import SearchSystem
from handlers.Handler import QuestionAnswerHandler, BlockHandler,StartHandler

def make_app(searching):
    return Application([
        (r"/qabot/question-answer", QuestionAnswerHandler, dict(searching=searching)),
        (r"/qabot/blocklist", BlockHandler, dict(searching=searching)),
    ])

if __name__ == "__main__":
    searching = SearchSystem(config="config.json")
    app = make_app(searching)
    app.listen(9091)
    tornado.ioloop.IOLoop.current().start()