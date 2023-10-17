import os
from Log.log import log
import SearchSystem.tools as tools
from SearchSystem.DataManager import DataForm

class Chain:
    def __init__(self):
        pass

    def init(self):
        pass

    def retrieve(self, question, docs:list[DataForm]):
        pass

def ChainFactory(environment)->Chain:
    if environment is not None:
        from transformers import AutoTokenizer, AutoModel

        class ChainGov(Chain):
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
                    self.tokenizer = AutoTokenizer.from_pretrained('/jingmen/chatglm-6b', trust_remote_code=True)
                    self.chain = AutoModel.from_pretrained('/jingmen/chatglm-6b', trust_remote_code=True).half().cuda()
                    self.chain = self.chain.eval()
                    log.info("loading finished")

            def retrieve(self, question, docs:list[DataForm]):
                context = '\n'
                for i, doc in enumerate(docs):
                    # context + docs + question length should be less than 1500
                    if len(self.prompt_template)+ len(context) + len(doc.title)+2+len(doc.page_content) + len(question) < 1500:
                        context += f'{doc.title}\n{doc.page_content}\n'
                    else:
                        docs = docs[:i]
                        break

                prompt = self.prompt_template.format(context=context, question=question)
                response, history = self.chain.chat(self.tokenizer, prompt, history=[])
                return response[0],docs
        return  ChainGov()
    else :
        from langchain.prompts import PromptTemplate
        from langchain.embeddings.openai import OpenAIEmbeddings
        from langchain.embeddings.openai import OpenAIEmbeddings
        from langchain.text_splitter import CharacterTextSplitter
        from langchain.chains import RetrievalQA
        # from langchain.llms import ChatOpenAI as OpenAI
        from langchain.chat_models import ChatOpenAI as OpenAI
        from langchain.vectorstores import Chroma
        from langchain.document_loaders import PyPDFLoader
        from langchain.document_loaders import Docx2txtLoader
        from rouge import Rouge

        import openai as BaseOpenAI

        from langchain.document_loaders.base import BaseLoader
        from langchain.docstore.document import Document
        from SearchSystem.DataManager import  SqlDataManager
        from langchain.prompts import PromptTemplate

        class ChainWeb(Chain):
            def __init__(self):
                self.prompt_template = """
                你现在是一个经验丰富，十分严谨的12345热线工作人员，负责解答市民的各种问题。现在，你会得到一份 背景知识 ，里面包括了回答市民问题所需要相关的知识。
                你必须礼貌，准确，严谨，无遗漏地根据这份知识来回答用户的问题，尽量使用这份知识的原文，不要遗漏原文的每一句话。按照给的资料的顺序，在使用到参考文献的地方标出参考文献角标，如[1]。
                不要列出参考文献列表。
                如果你不知道答案，只回答"未找到答案"，不要编造答案。如果你的答案不是来自 背景知识 ，只回答"未找到答案"，不要根据你已有的知识回答。
                你必须使用中文回答。

                背景知识: {context}

                问题: {question}
                中文答案:"""

                self.api_key = ""
                self.embeddings = None
                self.text_splitter = CharacterTextSplitter(separator="。", chunk_size=300, chunk_overlap=0)
                self.docsearch = None
                self.chain = None
                self.persist_directory = tools.searchSystemPath('db')
                self.init()

            def init(self):
                self.api_key = self.get_api_key()
                self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
                self.embedding()
                self.chain_type_kwargs = {"prompt": PromptTemplate(template=self.prompt_template, input_variables=["context", "question"])}
                self.chain = RetrievalQA.from_chain_type(llm=OpenAI(model_name="gpt-3.5-turbo-16k-0613", max_tokens=500, temperature=0), chain_type="stuff", retriever=self.docsearch.as_retriever(search_kwargs={'k': 5}), chain_type_kwargs=self.chain_type_kwargs, verbose=True, return_source_documents=True)

            def get_api_key(self):
                if self.api_key.startswith("sk-"):
                    return self.api_key
                else:
                    if os.getenv("OPENAI_API_KEY") is not None:
                        self.api_key = os.getenv("OPENAI_API_KEY")
                        return self.api_key
                    else:
                        log.info('请在openai官网注册账号，获取api_key填写至程序内或命令行参数中')
                        exit()

            def embedding(self):
                if tools.getConfig("new_embedding") == False:
                    self.docsearch = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
                    return

                loader = self.chain_loader()
                split_docs = loader.load()
                if len(split_docs) > 0:
                    if self.docsearch is None:
                        self.docsearch = Chroma.from_documents(split_docs, self.embeddings, persist_directory=self.persist_directory)
                    else:
                        self.docsearch.add_documents(split_docs)

                tools.setConfig("new_embedding", False)

            def chain_loader(self):
                class ChainLoader(BaseLoader):
                    def __init__(self) -> None:
                        super().__init__()

                    def load(self) -> list:
                        docs = []
                        datamanager = SqlDataManager()
                        for item in datamanager:
                            meta = item.metadata
                            meta["docId"] = item.docId
                            meta["title"] = item.title
                            for key in meta:
                                if meta[key] is None:
                                    meta[key] = ""
                            doc = Document(page_content=item.title + "\n\n" + item.page_content, metadata=meta)
                            if len(doc.page_content) > 1000:
                                log.info(f'{item.title} is too long, {doc}')
                            else:
                                docs.extend(self.text_splitter.split_documents([doc]))
                        return docs

                return ChainLoader()

            def retrieve(self, question,docs:list[DataForm]=[]):
                return self.chain({'query': question})["result"]
        return ChainWeb()
