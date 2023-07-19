namespace java com.kuaijie.customerservice.knowledge

// 知识问答输入
struct QuestionAnswerRequest {
    1: optional string question;
    2: optional string staffId;
    3: optional i32 isGenerate;
}

// 知识检索出的问答对
struct QuestionAnswerPair {
    1: optional string question;
    2: optional string answer;
    3: optional string source;
    4: optional string questionAnswerId;
}

// 知识生成文件信息
struct FileSourceInfo {
    1: optional string fileName;
    2: optional string fileLink;
    3: optional string referenceFragment;
}

// 知识生产答案
struct GenerateAnswer {
    1: optional string answer;
    // key引用下标    value是FileSourceInfo
    2: optional map<string,FileSourceInfo> source;
}

struct QuestionAnswerResult {
    1: optional list<QuestionAnswerPair> questionAnswerPairs;
    2: optional GenerateAnswer generateAnswers;
}

// 知识问答输出
struct QuestionAnswerResponse {
    // 错误状态码、以及错误信息描述
    // 0：正常返回；1：输入请求异常；2：服务内部错误（重试可能有效）
    1: optional i64 errCode=0;

    2: optional string errMsg;
    // 响应结果
    3: optional QuestionAnswerResult results;
}

