"""
🎯 FastAPI 실습: LangChain RAG 시스템 구축
1. ChromaDB 벡터 저장소를 활용한 문서 임베딩 및 검색
2. LCEL(LangChain Expression Language) 체인 구성 패턴
3. Retriever → Prompt → LLM → Parser 파이프라인 
4. 강의계획서 기반 Q&A 챗봇 API 구현

⚠️ Python 버전 주의:
- Python 3.14와 ChromaDB 호환 이슈 있음!
- Python 3.12 버전 또는 이전 버전 사용 권장
 
📌 사전 준비:
1. pip install fastapi uvicorn langchain-openai langchain-community langchain-core langgraph chromadb tiktoken
2. .env 파일에 OPENAI_API_KEY=sk-xxx 추가

📌 실행 방법:
python ./lab4/rag_qa.py

💡 RAG 파이프라인 흐름:
┌─────────┐    ┌───────────┐    ┌────────┐    ┌─────┐    ┌────────┐
│ Question │ → │ Retriever │ → │ Prompt │ → │ LLM │ → │ Answer │
└─────────┘    └───────────┘    └────────┘    └─────┘    └────────┘
                  (검색)         (컨텍스트      (GPT)     (문자열)
                                  + 질문)

"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

# LangChain v0.1 Core Imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# VectorStore & Document
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 1. 지식 베이스 (강의계획서라고 가정)
syllabus_text = """
[FastAPI 및 AI 웹 개발 과정]
1주차: Python 기초 및 FastAPI 기본 구조 (Hello World, Path Param)
2주차: Pydantic 데이터 검증 및 비동기 처리 (Async/Await)
3주차: Hugging Face Transformers 활용 (감성분석, 이미지 분류)
4주차: OpenAI API 및 LangChain 기초 (RAG, Prompt Engineering)
5주차: LangGraph 에이전트 및 Streamlit 실습
평가 방법: 출석 20%, 중간 과제 30%, 최종 프로젝트 50%
"""

# 전역 변수로 체인 
rag_chain = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 벡터 DB 구축 및 RAG 체인 생성 중...")
    global rag_chain

    # 1. 문서 생성
    docs = [Document(page_content=syllabus_text, metadata={"source": "강의계획서"})]
    # 2. 임베딩 및 벡터 저장소 생성 
    # vectorstore = Chroma.from_documents(
    #     documents=docs,
    #     embedding=OpenAIEmbeddings(),
    #     collection_name="course_syllabus"
    # )
    # OpenAIEmbeddings()를 아무 옵션 없이 호출하면, 내부적으로 기본 모델을 text-embedding-ada-002로 설정
    # 권장: 최신 임베딩 모델 사용 
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small") 
    # 또는 더 정밀한 모델 
    # embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="course_syllabus"
    )

    retriever = vectorstore.as_retriever()

    # 3. 프롬프트 템플릿 
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    # model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
    model = ChatOpenAI(model="gpt-5-mini", api_key=os.getenv("OPENAI_API_KEY"))

    # 4. LCEL 체인 구성 (Retriever -> Context 병합 -> Prompt -> LLM -> String)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    print("✅ RAG 시스템 준비 완료!")
    yield
    print("🛑 시스템 종료")

app = FastAPI(lifespan=lifespan)

class QuestionRequest(BaseModel):
    question: str

@app.post("/qa")
async def qa(request: QuestionRequest):
    if rag_chain is None:
        raise HTTPException(status_code=500, detail="RAG 체인 초기화 중 오류 발생")
    try:
        result = await rag_chain.invoke({"question": request.question})
        return {"answer": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask-syllabus")
async def ask_syllabus(req: QuestionRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG Chain not init")
    
    # 체인 실행(ainvoke): # 비동기(async)로 RAG 체인을 실행하고 완료될 때까지 기다린 뒤 결과를 받음
    response = await rag_chain.ainvoke(req.question)
    return {"answer": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)