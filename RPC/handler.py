import QuestionAnswerServer.QuestionAnswerServer as QuestionAnswerServer
import QuestionAnswerServer.BlockListService as BlockHandlerServer
from SearchSystem import searchSystem 
from SearchSystem.DataManager import DataForm
from QuestionAnswer.ttypes import QuestionAnswerPair, QuestionAnswerRequest, QuestionAnswerResponse, QuestionAnswerResult,FileSourceInfo,GenerateAnswer
from Log.log import log

searching = searchSystem.SearchSyetem(config="config.json")


class QuestionAnswerHandler(QuestionAnswerServer.Iface):
    def searchAndGeneration(self, request: QuestionAnswerRequest) -> QuestionAnswerResponse:
        log.info(f'QuestionAnswerHandler searchAndGeneration: question:{request.question},isGenerate:{request.isGenerate}')
        sources={
            101:"用户上传",
            102:"通话生成",
            103:"知识文件",
            104:"历史工单"
        }
        if request.isGenerate == 0:
            log.info(f'not generate {request.question}')
            qaList = []
            search_res:list[DataForm] = searching.searchResults(request.question)
            for item in search_res:
                # 判断sourceunit，基于item.metadata["from"]的值，判断来源


                qaList.append(
                    QuestionAnswerPair(
                        question=item.title,
                        answer=item.page_content,
                        source=sources[item.metadata["from"]],
                        questionAnswerId=str(item.docId),
                        sourceUnit="",
                        # TODO 这是啥呀？
                        knowledgeFileSource=None
                    )
                )
            log.info(f'questions:{[x.question for x in qaList]},answers:{[x.answer for x in qaList]}')
            response = QuestionAnswerResponse(
                errCode=0,
                errMsg="SUCCESS",
                results=QuestionAnswerResult(
                    questionAnswerPairs=qaList
                )
            )
            return response
        
        elif request.isGenerate == 1:
            log.info(f'generate {request.question}')
            qaPair:list[QuestionAnswerPair]=[]
            search_res:list[DataForm]
            answer,search_res,fragment = searching.searchResults(request.question,choice=7)
            answer=answer.split("参考文献")[0]
            for i,item in enumerate(search_res):
                qaPair.append(
                    QuestionAnswerPair(
                        question=item.title,
                        answer=item.page_content,
                        source=sources[item.metadata["from"]],
                        questionAnswerId=str(item.docId),
                        sourceUnit="",
                        # TODO 这是啥呀？
                        knowledgeFileSource=None
                    )
                )

            response =  QuestionAnswerResponse(
                errCode=0,
                errMsg="SUCCESS",
                results=QuestionAnswerResult(
                    generateAnswers=GenerateAnswer(
                        answer=answer,
                        questionAnswerPairs=qaPair
                    )
                )
            )
            return response

        else:
            log.info(f'isGenerate参数错误,需要为0或者1')
            response = QuestionAnswerResponse(errCode=1, errMsg="isGenerate参数错误,需要为0或者1",results=None)
            return response
    
class BlockHandler(BlockHandlerServer.Iface):
    def addBlockList(self, addList):
        log.info(f"BlockList add: {addList}")
        searching.block(addList)