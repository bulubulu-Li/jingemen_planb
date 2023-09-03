#
# Autogenerated by Thrift Compiler (0.12.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys

from thrift.transport import TTransport
all_structs = []


class QuestionAnswerRequest(object):
    """
    Attributes:
     - question
     - staffId
     - isGenerate

    """


    def __init__(self, question=None, staffId=None, isGenerate=None,):
        self.question = question
        self.staffId = staffId
        self.isGenerate = isGenerate

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.question = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.staffId = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.I32:
                    self.isGenerate = iprot.readI32()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('QuestionAnswerRequest')
        if self.question is not None:
            oprot.writeFieldBegin('question', TType.STRING, 1)
            oprot.writeString(self.question.encode('utf-8') if sys.version_info[0] == 2 else self.question)
            oprot.writeFieldEnd()
        if self.staffId is not None:
            oprot.writeFieldBegin('staffId', TType.STRING, 2)
            oprot.writeString(self.staffId.encode('utf-8') if sys.version_info[0] == 2 else self.staffId)
            oprot.writeFieldEnd()
        if self.isGenerate is not None:
            oprot.writeFieldBegin('isGenerate', TType.I32, 3)
            oprot.writeI32(self.isGenerate)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class QuestionAnswerPair(object):
    """
    Attributes:
     - question
     - answer
     - source
     - questionAnswerId
     - sourceUnit
     - knowledgeFileSource

    """


    def __init__(self, question=None, answer=None, source=None, questionAnswerId=None, sourceUnit=None, knowledgeFileSource=None,):
        self.question = question
        self.answer = answer
        self.source = source
        self.questionAnswerId = questionAnswerId
        self.sourceUnit = sourceUnit
        self.knowledgeFileSource = knowledgeFileSource

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.question = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.answer = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRING:
                    self.source = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.STRING:
                    self.questionAnswerId = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.STRING:
                    self.sourceUnit = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.LIST:
                    self.knowledgeFileSource = []
                    (_etype3, _size0) = iprot.readListBegin()
                    for _i4 in range(_size0):
                        _elem5 = FileSourceInfo()
                        _elem5.read(iprot)
                        self.knowledgeFileSource.append(_elem5)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('QuestionAnswerPair')
        if self.question is not None:
            oprot.writeFieldBegin('question', TType.STRING, 1)
            oprot.writeString(self.question.encode('utf-8') if sys.version_info[0] == 2 else self.question)
            oprot.writeFieldEnd()
        if self.answer is not None:
            oprot.writeFieldBegin('answer', TType.STRING, 2)
            oprot.writeString(self.answer.encode('utf-8') if sys.version_info[0] == 2 else self.answer)
            oprot.writeFieldEnd()
        if self.source is not None:
            oprot.writeFieldBegin('source', TType.STRING, 3)
            oprot.writeString(self.source.encode('utf-8') if sys.version_info[0] == 2 else self.source)
            oprot.writeFieldEnd()
        if self.questionAnswerId is not None:
            oprot.writeFieldBegin('questionAnswerId', TType.STRING, 4)
            oprot.writeString(self.questionAnswerId.encode('utf-8') if sys.version_info[0] == 2 else self.questionAnswerId)
            oprot.writeFieldEnd()
        if self.sourceUnit is not None:
            oprot.writeFieldBegin('sourceUnit', TType.STRING, 5)
            oprot.writeString(self.sourceUnit.encode('utf-8') if sys.version_info[0] == 2 else self.sourceUnit)
            oprot.writeFieldEnd()
        if self.knowledgeFileSource is not None:
            oprot.writeFieldBegin('knowledgeFileSource', TType.LIST, 6)
            oprot.writeListBegin(TType.STRUCT, len(self.knowledgeFileSource))
            for iter6 in self.knowledgeFileSource:
                iter6.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class FileSourceInfo(object):
    """
    Attributes:
     - fileName
     - fileLink

    """


    def __init__(self, fileName=None, fileLink=None,):
        self.fileName = fileName
        self.fileLink = fileLink

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.fileName = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.fileLink = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('FileSourceInfo')
        if self.fileName is not None:
            oprot.writeFieldBegin('fileName', TType.STRING, 1)
            oprot.writeString(self.fileName.encode('utf-8') if sys.version_info[0] == 2 else self.fileName)
            oprot.writeFieldEnd()
        if self.fileLink is not None:
            oprot.writeFieldBegin('fileLink', TType.STRING, 2)
            oprot.writeString(self.fileLink.encode('utf-8') if sys.version_info[0] == 2 else self.fileLink)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class GenerateAnswer(object):
    """
    Attributes:
     - answer
     - questionAnswerPairs

    """


    def __init__(self, answer=None, questionAnswerPairs=None,):
        self.answer = answer
        self.questionAnswerPairs = questionAnswerPairs

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.answer = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.LIST:
                    self.questionAnswerPairs = []
                    (_etype10, _size7) = iprot.readListBegin()
                    for _i11 in range(_size7):
                        _elem12 = QuestionAnswerPair()
                        _elem12.read(iprot)
                        self.questionAnswerPairs.append(_elem12)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('GenerateAnswer')
        if self.answer is not None:
            oprot.writeFieldBegin('answer', TType.STRING, 1)
            oprot.writeString(self.answer.encode('utf-8') if sys.version_info[0] == 2 else self.answer)
            oprot.writeFieldEnd()
        if self.questionAnswerPairs is not None:
            oprot.writeFieldBegin('questionAnswerPairs', TType.LIST, 2)
            oprot.writeListBegin(TType.STRUCT, len(self.questionAnswerPairs))
            for iter13 in self.questionAnswerPairs:
                iter13.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class QuestionAnswerResult(object):
    """
    Attributes:
     - questionAnswerPairs
     - generateAnswers

    """


    def __init__(self, questionAnswerPairs=None, generateAnswers=None,):
        self.questionAnswerPairs = questionAnswerPairs
        self.generateAnswers = generateAnswers

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.LIST:
                    self.questionAnswerPairs = []
                    (_etype17, _size14) = iprot.readListBegin()
                    for _i18 in range(_size14):
                        _elem19 = QuestionAnswerPair()
                        _elem19.read(iprot)
                        self.questionAnswerPairs.append(_elem19)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRUCT:
                    self.generateAnswers = GenerateAnswer()
                    self.generateAnswers.read(iprot)
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('QuestionAnswerResult')
        if self.questionAnswerPairs is not None:
            oprot.writeFieldBegin('questionAnswerPairs', TType.LIST, 1)
            oprot.writeListBegin(TType.STRUCT, len(self.questionAnswerPairs))
            for iter20 in self.questionAnswerPairs:
                iter20.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.generateAnswers is not None:
            oprot.writeFieldBegin('generateAnswers', TType.STRUCT, 2)
            self.generateAnswers.write(oprot)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class QuestionAnswerResponse(object):
    """
    Attributes:
     - errCode
     - errMsg
     - results

    """


    def __init__(self, errCode=0, errMsg=None, results=None,):
        self.errCode = errCode
        self.errMsg = errMsg
        self.results = results

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.I64:
                    self.errCode = iprot.readI64()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.errMsg = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRUCT:
                    self.results = QuestionAnswerResult()
                    self.results.read(iprot)
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('QuestionAnswerResponse')
        if self.errCode is not None:
            oprot.writeFieldBegin('errCode', TType.I64, 1)
            oprot.writeI64(self.errCode)
            oprot.writeFieldEnd()
        if self.errMsg is not None:
            oprot.writeFieldBegin('errMsg', TType.STRING, 2)
            oprot.writeString(self.errMsg.encode('utf-8') if sys.version_info[0] == 2 else self.errMsg)
            oprot.writeFieldEnd()
        if self.results is not None:
            oprot.writeFieldBegin('results', TType.STRUCT, 3)
            self.results.write(oprot)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(QuestionAnswerRequest)
QuestionAnswerRequest.thrift_spec = (
    None,  # 0
    (1, TType.STRING, 'question', 'UTF8', None, ),  # 1
    (2, TType.STRING, 'staffId', 'UTF8', None, ),  # 2
    (3, TType.I32, 'isGenerate', None, None, ),  # 3
)
all_structs.append(QuestionAnswerPair)
QuestionAnswerPair.thrift_spec = (
    None,  # 0
    (1, TType.STRING, 'question', 'UTF8', None, ),  # 1
    (2, TType.STRING, 'answer', 'UTF8', None, ),  # 2
    (3, TType.STRING, 'source', 'UTF8', None, ),  # 3
    (4, TType.STRING, 'questionAnswerId', 'UTF8', None, ),  # 4
    (5, TType.STRING, 'sourceUnit', 'UTF8', None, ),  # 5
    (6, TType.LIST, 'knowledgeFileSource', (TType.STRUCT, [FileSourceInfo, None], False), None, ),  # 6
)
all_structs.append(FileSourceInfo)
FileSourceInfo.thrift_spec = (
    None,  # 0
    (1, TType.STRING, 'fileName', 'UTF8', None, ),  # 1
    (2, TType.STRING, 'fileLink', 'UTF8', None, ),  # 2
)
all_structs.append(GenerateAnswer)
GenerateAnswer.thrift_spec = (
    None,  # 0
    (1, TType.STRING, 'answer', 'UTF8', None, ),  # 1
    (2, TType.LIST, 'questionAnswerPairs', (TType.STRUCT, [QuestionAnswerPair, None], False), None, ),  # 2
)
all_structs.append(QuestionAnswerResult)
QuestionAnswerResult.thrift_spec = (
    None,  # 0
    (1, TType.LIST, 'questionAnswerPairs', (TType.STRUCT, [QuestionAnswerPair, None], False), None, ),  # 1
    (2, TType.STRUCT, 'generateAnswers', [GenerateAnswer, None], None, ),  # 2
)
all_structs.append(QuestionAnswerResponse)
QuestionAnswerResponse.thrift_spec = (
    None,  # 0
    (1, TType.I64, 'errCode', None, 0, ),  # 1
    (2, TType.STRING, 'errMsg', 'UTF8', None, ),  # 2
    (3, TType.STRUCT, 'results', [QuestionAnswerResult, None], None, ),  # 3
)
fix_spec(all_structs)
del all_structs