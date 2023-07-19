include "QuestionAnswer.thrift"
namespace java com.kuaijie.customerservice.knowledge

service QuestionAnswerServer {

    // 对外接口：工单摘要
    QuestionAnswer.QuestionAnswerResponse searchAndGeneration(
        1: required QuestionAnswer.QuestionAnswerRequest request
    );

}