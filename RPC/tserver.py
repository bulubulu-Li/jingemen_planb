from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
# import the project into python path
import sys
import os
# 获取当前路径，取出'jingemen_planb'和其前部为项目路径
projectpath = os.path.abspath(__file__)
projectpath = projectpath[:projectpath.find('jingemen_planb') + len('jingemen_planb')]
print(f'projectpath is {projectpath}')
sys.path.append(projectpath)
import QuestionAnswerServer.QuestionAnswerServer as QuestionAnswerServer
import handler as Handler

# handler = Handler.QuestionAnswerHandler()
# processor = QuestionAnswerServer.Processor(handler)
# transport = TSocket.TServerSocket(port=9090)
# tfactory = TTransport.TBufferedTransportFactory()
# pfactory = TBinaryProtocol.TBinaryProtocolFactory()

# server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

# print("Starting python server...")
# server.serve()
# print("done!")



__HOST = '127.0.0.1'
__PORT = 9091


if __name__ == '__main__':
    handler = Handler.QuestionAnswerHandler()
    processor = QuestionAnswerServer.Processor(handler)
    transport = TSocket.TServerSocket(port=__PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    # tfactory = TTransport.TFramedTransportFactory()
    # pfactory = TCompactProtocol.TCompactProtocolFactory()
    # rpcServer = TServer.TSimpleServer(processor,transport, tfactory, pfactory)
    rpcServer = TServer.TThreadPoolServer(processor,transport, tfactory, pfactory)
    # rpcServer = TServer.TThreadedSelectorServer(processor,transport, tfactory, pfactory)
    rpcServer.setNumThreads(5)
    print('Starting the rpc server at:', __PORT)
    #print('Starting the rpc server at', __HOST,':', __PORT)
    rpcServer.serve()
