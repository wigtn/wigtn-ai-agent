from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
import operator

# 도구 호출
from tools import tools

# 환경 변수 로드
import dotenv
dotenv.load_dotenv()

# State 정의
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# LLM에 도구 바인딩
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
llm_with_tools = llm.bind_tools(tools)

tools_by_name = {tool.name: tool for tool in tools}

# Node: Agent
def agent_node(state: AgentState):
    """에이전트 노드: LLM이 다음 행동을 결정"""
    # 현재 대화 기록
    messages = state["messages"]

    # LLM 호출
    response = llm_with_tools.invoke(messages)

    # State 업데이트
    return {'messages': [response]}

# Node: Tools Node
def tools_node(state: AgentState):
    """도구 실행 노드: LLM이 도구를 호출"""
    # 마지막 메시지
    last_message = state["messages"][-1]

    # 도구 호출이 없으면 빈 딕셔너리 반환
    if not last_message.tool_calls:
        return {}

    # 도구 실행 결과를 담을 리스트
    tool_messages = []

    # 여러 도구 호출이 있을 수 있으므로 반복
    for tool_call in last_message.tool_calls:
        # 도구 이름과 인자 추출
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # 도구 찾기
        tool = tools_by_name[tool_name]
        result = tool.invoke(tool_args)

        # 결과를 ToolMessage로 감싸기
        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
                )
            )
        
        # State Update: 도구 실행
        return {"messages": tool_messages}

# Node: Routing Edge
def should_continue(state: AgentState) -> Literal["tools", END]:
        "도구를 실행할지, 종료할지 결정"

        # 마지막 메시지
        last_message = state["messages"][-1]

        # LLM이 도구를 호출 했는지 확인
        if last_message.tool_calls:
            return "tools"

        return END  

# StateGraph
graph_builder = StateGraph(AgentState)

# 노드 추가
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tools_node)

# Edge 추가
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    }
)
graph_builder.add_edge("tools", "agent")

# Compile
app = graph_builder.compile()

# 실행
def run_agent():
    print("랭그래프 에이전트 시작! (종료: quit, exit, q)")
    print("-"*50)

    while True:
        user_input = input("\nYou:")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        result = app.invoke(
            {
                "messages": [HumanMessage(content=user_input)]
            }
        )

        final_message = result["messages"][-1]
        print(f"\nAssistant: {final_message.content}")

if __name__ == "__main__":
    run_agent()


