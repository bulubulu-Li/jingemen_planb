include "QuestionAnswer.thrift"
namespace java com.kuaijie.customerservice.knowledge

service QuestionAnswerServer {

    // 对外接口：工单摘要
    QuestionAnswer.QuestionAnswerResponse searchAndGeneration(
        1: required QuestionAnswer.QuestionAnswerRequest request
    );

}
service BlockListService {

    // inParam:
    //  addList: 传入的需要放入黑名单中的知识对id
    // outParam: 本次成功加入黑名单的知识对id数量
    i32 addBlockList(1: list<i32> addList);
}