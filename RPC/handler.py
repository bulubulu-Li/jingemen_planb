import QuestionAnswerServer.QuestionAnswerServer as QuestionAnswerServer
from SearchSystem import main as searching
from SearchSystem.DataManager import DataForm
from QuestionAnswer.ttypes import QuestionAnswerPair, QuestionAnswerRequest, QuestionAnswerResponse, QuestionAnswerResult,FileSourceInfo,GenerateAnswer


class QuestionAnswerHandler(QuestionAnswerServer.Iface):
    def searchAndGeneration(self, request: QuestionAnswerRequest) -> QuestionAnswerResponse:

        if request.isGenerate == 0:
            print(f'not generate {request.question}')
            qaList = []
            search_res:list[DataForm] = searching.searchResults(request.question)
            for item in search_res:
                qaList.append(
                    QuestionAnswerPair(
                        question=item.title,
                        answer=item.page_content,
                        source="历史问答对上传"
                    )
                )

            return QuestionAnswerResponse(
                errCode=0,
                errMsg="SUCCESS",
                results=QuestionAnswerResult(
                    questionAnswerPairs=qaList
                )
            )
        
        elif request.isGenerate == 1:
            print(f'generate {request.question}')
            qaList = {}
            search_res:list[DataForm]
            answer,search_res,fragment = searching.searchResults(request.question,choice=7)
            answer=answer.split("参考文献")[0]
            for i,item in enumerate(search_res):
                qaList[f"[{i+1}]"]=FileSourceInfo(
                    # fileLink=f'title:{item.title}, url:{item.metadata["url"]}, doc:{item.docId}',
                    fileLink=f'url:{item.metadata["url"]}, doc:{item.docId}',
                    fileName=item.title,
                    referenceFragment=fragment[i],
                )
            return QuestionAnswerResponse(
                errCode=0,
                errMsg="SUCCESS",
                results=QuestionAnswerResult(
                    generateAnswers=GenerateAnswer(
                        answer=answer,
                        source=qaList
                    )
                )
            )

        else:
            print(f'isGenerate参数错误,需要为0或者1')
            return QuestionAnswerResponse(errCode=1, errMsg="isGenerate参数错误,需要为0或者1",results=None)
    