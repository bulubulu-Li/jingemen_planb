import tornado.ioloop
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
from tornado.options import options, define
from multiprocessing import Process

# Import the project into python path
import sys
import os

# 获取当前路径，取出'jingemen_planb'和其前部为项目路径
projectpath = os.path.abspath(__file__)
projectpath = projectpath[:projectpath.find('jingemen_planb') + len('jingemen_planb')]
print(f'projectpath is {projectpath}')
sys.path.append(projectpath)

from SearchSystem.searchSystem import SearchSystem
from handlers.Handler import QuestionAnswerHandler, BlockHandler,StartHandler

def launch_service(config):
    searching = SearchSystem(config="config.json")

    process_test_class_1 = Process(target=QuestionAnswerHandler, args=(config["process_test_class_1"], searching))
    process_test_class_2 = Process(target=BlockHandler, args=(config["process_test_class_2"], searching))

    processes = [process_test_class_1, process_test_class_2]
    print("start")
    for process in processes:
        process.start()
    for process in processes:
        process.join()

if __name__ == "__main__":
    config = {"process_test_class_1":{"port":3130, "url_suffix":"/a"},
              "process_test_class_2":{"port":3131, "url_suffix":"/b"}}
    launch_service(config)