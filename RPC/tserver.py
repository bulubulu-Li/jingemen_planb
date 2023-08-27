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
__PORT = 9091

if __name__ == '__main__':
    # Handlers
    question_answer_handler = Handler.QuestionAnswerHandler()
    block_handler = Handler.BlockHandler()
    
    # Processors
    question_answer_processor = QuestionAnswerServer.Processor(question_answer_handler)
    block_processor = BlockListService.Processor(block_handler)
    
    # Multiplexed Processor
    multiplexed_processor = TMultiplexedProcessor()
    multiplexed_processor.registerProcessor("QuestionAnswerService", question_answer_processor)
    multiplexed_processor.registerProcessor("BlockListService", block_processor)
    
    # Server setup
    transport = TSocket.TServerSocket(port=__PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    
    # Use TThreadPoolServer for multi-threading
    rpcServer = TServer.TThreadPoolServer(multiplexed_processor, transport, tfactory, pfactory)
    rpcServer.setNumThreads(5)
    
    print(f'Starting the rpc server at port: {__PORT}')
    rpcServer.serve()
