"""
🎯 FastAPI 실습: LangGraph 조건부 라우팅 에이전트
1. LangGraph StateGraph를 활용한 워크플로우 구성
2. 조건부 엣지(Conditional Edges)로 동적 라우팅 구현
3. 질문 유형에 따라 다른 페르소나(전문가/친구)로 응답
4. TypedDict를 사용한 상태(State) 관리 패턴

📌 사전 준비:
1. pip install fastapi uvicorn langgraph langchain-openai langchain-core
2. .env 파일에 OPENAI_API_KEY=sk-xxx 추가

📌 실행 방법:
python ./lab4/langgraph_qa.py


📌 테스트 (Swagger UI):
http://localhost:8000/docs → /smart_chat → Try it out
message 예제1: "파이썬에서 데코레이터가 뭐야?"
message 예제2: "오늘 날씨 어때?"

💡 LangGraph 워크플로우 구조:
                    ┌─────────────┐
                    │  classifier │ (질문 분류)
                    └──────┬──────┘
                           │
            ┌──────────────┴──────────────┐
            │ TECHNICAL          CASUAL   │
            ▼                             ▼
    ┌──────────────┐              ┌─────────────┐
    │ tech_expert  │              │ friendly_bot│
    │ (시니어 개발자)│              │ (친절한 친구) │
    └──────┬───────┘              └──────┬──────┘
           │                             │
           └──────────────┬──────────────┘
                          ▼
                        [END]

"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import TypedDict, Literal

# LangGraph & LangChain Imports
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = FastAPI()

# 1. 상태(State) 정의: 그래프 내에서 공유되는 데이터
class AgentState(TypedDict):
    question: str
    classification: str
    response: str

# 2. 모델 설정
# model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
model = ChatOpenAI(model_name="gpt-5-mini", api_key=os.getenv("OPENAI_API_KEY"))

# --- 노드(Nodes) 정의 ---
# 노드 1: 질문 분류기 (Classifier)
def classify_input(state: AgentState):
    print(f"--- 분류중: {state['question']}")
    prompt = ChatPromptTemplate.from_template(
        """다음 질문을 'TECHNICAL'(프로그래밍/코딩/기술 관련) 또는 'CASUAL'(일상 대화/인사) 중 하나로 분류하세요.
            질문: {question}
            결과:
        """
        )
    chain = prompt | model | StrOutputParser()
    result = chain.invoke({"question": state["question"]})

    # 결과를 깔끔하게 정제
    classification = "TECHNICAL" if "TECHNICAL" in result.upper() else "CASUAL"
    return {"classification": classification}

# 노드 2: 기술 전문가 답변
def handle_technical(state: AgentState):
    print("=========== 기술 전문가 모드")
    prompt = ChatPromptTemplate.from_template(
        "당신은 시니어 파이썬 개발자입니다. 질문에 대해 명확하고 엄격하게 답변하세요.\n질문: {question}"
    )
    chain = prompt | model | StrOutputParser()
    return {"response": chain.invoke({"question": state['question']})}
   
# 노드 3: 친절한 친구 답변
def handle_casual(state: AgentState):
    print("=========== 일상 대화 모드")
    prompt = ChatPromptTemplate.from_template(
        "당신은 친절한 친구입니다. 이모지를 사용해서 따뜻하게 답변하세요.\n질문: {question}"
    )
    chain = prompt | model | StrOutputParser()
    return {"response": chain.invoke({"question": state['question']})}


# --- 그래프(Graph) 구성 ---
workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("classifier", classify_input)
workflow.add_node("tech_expert", handle_technical)
workflow.add_node("friendly_bot", handle_casual)

# 진입점 설정
workflow.set_entry_point("classifier")

# 조건부 엣지 함수: 분류 결과에 따라 다음 노드 결정
def decide_route(state: AgentState):
    if state["classification"] == "TECHNICAL":
        return "tech_expert"
    else:
        return "friendly_bot"
    
# 조건부 엣지 연결 (classifier -> tech_expert OR friendly_bot)
workflow.add_conditional_edges(
    "classifier",
    decide_route,
    {
        "tech_expert": "tech_expert",
        "friendly_bot": "friendly_bot"
    }
)

# 종료 엣지 연결
workflow.add_edge("tech_expert", END)
workflow.add_edge("friendly_bot", END)

# 그래프 컴파일 (실행 가능한 객체로 변환)
app_graph = workflow.compile()


# --- FastAPI 엔드포인트 ---
class ChatRequest(BaseModel):
    message: str

@app.post("/smart_chat")
async def smart_chat(req: ChatRequest):
    inputs = {"question": req.message}
    result = await app_graph.ainvoke(inputs)

    return {
        "type": result["classification"],
        "reply": result["response"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)