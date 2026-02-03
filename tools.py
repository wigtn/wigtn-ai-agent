from langchain_core.tools import tool
from tavily import TavilyClient
from datetime import datetime

import dotenv
dotenv.load_dotenv()

@tool
def get_current_time() -> str:
    """현재 시간을 반환합니다"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate(expression: str) -> str:
    """수식을 계산합니다."""
    try:
        result = eval(expression)
        return f"계산 결과: {result}"

    except Exception as e:
        return f"계산 중 오류가 발생했습니다: {e}"

tavily_client = TavilyClient()

@tool
def search_web(query: str) -> str:
    """웹에서 정보를 검색합니다."""
    try:
        response = tavily_client.search(query, max_results=3)
        print(f"[DEBUG] 검색 응답: {response.get('results', [])}")

        results = response.get('results', [])
        if not results:
            return "검색 결과가 없습니다"
        # 검색 결과 포매팅
        formatted_results = []
        for result in results:
            title = result.get('title', 'N/A')
            content = result.get('content', 'N/A')
            url = result.get('url', 'N/A')

            formatted_results.append(
                f"제목: {title}\n"
                f"내용: {content}\n"
                f"URL: {url}\n"
            )

        return "\n---\n".join(formatted_results)

    except Exception as e:
        print(f"[DEBUG] 검색 오류 상세: {e}")
        return f"검색 중 오류가 발생했습니다: {e}"

tools = [get_current_time, calculate, search_web]