import os
from Log.log import log
import SearchSystem.tools as tools

from transformers import AutoTokenizer, AutoModel

class Chain:
    def __init__(self):
        self.chain = None
        self.tokenizer = None
        self.prompt_template = """
        你现在是一个经验丰富，十分严谨的12345热线工作人员，负责解答市民的各种问题。现在，你会得到一份 背景知识 ，里面包括了回答市民问题所需要相关的知识。
        你必须礼貌，准确，严谨，无遗漏地根据这份知识来回答用户的问题，尽量使用这份知识的原文，不要遗漏原文的每一句话。按照给的资料的顺序，在使用到参考文献的地方标出参考文献角标，如[1]。
        不要列出参考文献列表。
        如果你不知道答案，只回答"未找到答案"，不要编造答案。如果你的答案不是来自 背景知识 ，只回答"未找到答案"，不要根据你已有的知识回答。
        你必须使用中文回答。

        背景知识: {context}

        问题: {question}
        中文答案:"""
        # self.init()

    def init(self):
        log.info('chain init!!!')
        if self.chain is None:
            log.info("chain is None,start loading")
            self.tokenizer = AutoTokenizer.from_pretrained(os.path.join(tools.searchSystemPath,'LargeLanguageModel/chatglm-6b'), trust_remote_code=True)
            self.chain = AutoModel.from_pretrained(os.path.join(tools.searchSystemPath,'LargeLanguageModel/chatglm-6b'), trust_remote_code=True).half().cuda()
            self.chain = self.chain.eval()
            log.info("loading finished")

    def retrieve(self, question, context):
        prompt = self.prompt_template.format(context=context, question=question)
        response, history = self.chain.chat(self.tokenizer, prompt, history=[])
        return response