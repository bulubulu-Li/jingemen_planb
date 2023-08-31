from thrift.transport import TSocket 
from thrift.transport import TTransport 
from thrift.protocol import TBinaryProtocol 
from thrift.server import TServer
from thrift.TMultiplexedProcessor import TMultiplexedProcessor

# Import the project into python path
import sys
import os

# 获取当前路径，取出'jingemen_planb'和其前部为项目路径
projectpath = os.path.abspath(__file__)
projectpath = projectpath[:projectpath.find('jingemen_planb') + len('jingemen_planb')]
print(f'projectpath is {projectpath}')
sys.path.append(projectpath)
import QuestionAnswerServer.QuestionAnswerServer as QuestionAnswerServer
import QuestionAnswerServer.BlockListService as BlockListService
import handler as Handler

__HOST = '127.0.0.1'
__PORT1 = 3030
__PORT2 = 9091

if __name__ == '__main__':
    # Handlers
    question_answer_handler = Handler.QuestionAnswerHandler()
    block_handler = Handler.BlockHandler()
    
    # Processors
    question_answer_processor = QuestionAnswerServer.Processor(question_answer_handler)
    block_processor = BlockListService.Processor(block_handler)
    
    # Server setup
    transport1 = TSocket.TServerSocket(port=__PORT1)
    transport2 = TSocket.TServerSocket(port=__PORT2)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    
    # Use TThreadPoolServer for multi-threading
    rpcServer1 = TServer.TThreadPoolServer(question_answer_processor, transport1, tfactory, pfactory)
    rpcServer1.setNumThreads(5)
    
    rpcServer2 = TServer.TThreadPoolServer(block_processor, transport2, tfactory, pfactory)
    rpcServer2.setNumThreads(5)
    
    print(f'Starting the rpc server at port: {__PORT1} for QuestionAnswerService')
    rpcServer1.serve()
    
    print(f'Starting the rpc server at port: {__PORT2} for BlockListService')
    rpcServer2.serve()