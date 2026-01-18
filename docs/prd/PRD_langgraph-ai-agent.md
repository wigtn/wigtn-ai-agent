# LangGraph AI Agent Chatbot 설계 PRD

> **Version**: 1.1
> **Created**: 2026-01-18
> **Updated**: 2026-01-18
> **Status**: Draft (Reviewed)

## 1. Overview

### 1.1 Problem Statement

AI 에이전트 기반 챗봇을 구축할 때, 단순한 LLM 호출을 넘어서 복잡한 워크플로우 관리, 상태 유지, 그리고 확장 가능한 Middleware 구조가 필요합니다. LangGraph의 `create_react_agent` 함수를 활용하여 ReAct 패턴 기반의 에이전트를 구축하고, Middleware를 통해 로깅, 검증, 에러 핸들링 등 횡단 관심사를 처리하는 아키텍처가 필요합니다.

### 1.2 Goals

- LangGraph의 `create_react_agent`를 사용한 ReAct 에이전트 구축
- 확장 가능한 Middleware 아키텍처 설계 및 구현
- 상태 관리와 메모리 기능을 갖춘 대화형 챗봇 구현
- 다양한 Tool을 플러그인 방식으로 연결할 수 있는 구조 설계

### 1.3 Non-Goals (Out of Scope)

- 프로덕션 배포 인프라 구성 (Kubernetes, Cloud 배포)
- 사용자 인증/인가 시스템 (별도 PRD로 분리)
- 웹 UI/프론트엔드 구현 (API 서버만 구현)
- 멀티 에이전트 오케스트레이션 (단일 에이전트 우선)

### 1.4 Scope

| 포함 | 제외 |
|------|------|
| LangGraph ReAct Agent 구현 | Multi-Agent 시스템 |
| Middleware 레이어 설계 | 프론트엔드 UI |
| Tool 플러그인 시스템 | 인증/인가 시스템 |
| 대화 상태 관리 (Memory) | 프로덕션 배포 |
| FastAPI 기반 API 서버 | 모니터링/알림 시스템 |
| 로컬 개발 환경 구성 | 부하 테스트 |

---

## 2. User Stories

### 2.1 Primary User: 개발자

**US-001**: 에이전트 초기화
> As a 개발자, I want to LangGraph create_react_agent로 에이전트를 쉽게 초기화할 수 있게 so that 복잡한 설정 없이 ReAct 패턴 에이전트를 사용할 수 있다.

**US-002**: Middleware 적용
> As a 개발자, I want to 에이전트 실행 전후에 Middleware를 적용할 수 있게 so that 로깅, 검증, 에러 핸들링 등을 일관되게 처리할 수 있다.

**US-003**: Tool 확장
> As a 개발자, I want to 새로운 Tool을 플러그인 방식으로 추가할 수 있게 so that 에이전트의 기능을 쉽게 확장할 수 있다.

### 2.2 Primary User: 최종 사용자 (챗봇 이용자)

**US-004**: 대화 연속성
> As a 사용자, I want to 이전 대화 내용을 기억하는 챗봇과 대화할 수 있게 so that 맥락 있는 대화가 가능하다.

**US-005**: Tool 활용 응답
> As a 사용자, I want to 챗봇이 필요한 경우 외부 Tool을 활용해 정확한 답변을 제공받을 수 있게 so that 단순 텍스트 응답을 넘어선 유용한 정보를 얻을 수 있다.

### 2.3 Acceptance Criteria (Gherkin)

```gherkin
Scenario: ReAct Agent가 Tool을 사용하여 질문에 답변
  Given 에이전트가 웹 검색 Tool과 함께 초기화되어 있다
  And Middleware 체인이 설정되어 있다
  When 사용자가 "오늘 서울 날씨 알려줘"라고 질문한다
  Then 에이전트는 웹 검색 Tool을 호출한다
  And 검색 결과를 바탕으로 날씨 정보를 응답한다
  And Middleware가 요청/응답을 로깅한다

Scenario: Middleware가 에러를 처리
  Given 에러 핸들링 Middleware가 활성화되어 있다
  When Tool 실행 중 예외가 발생한다
  Then Middleware가 예외를 캐치한다
  And 사용자 친화적인 에러 메시지를 반환한다
  And 에러 상세 정보를 로깅한다

Scenario: 대화 히스토리 유지
  Given 사용자가 thread_id "user-123"으로 대화를 시작했다
  And 첫 번째 메시지로 "내 이름은 홍길동이야"라고 말했다
  When 두 번째 메시지로 "내 이름이 뭐였지?"라고 질문한다
  Then 에이전트는 "홍길동"이라고 응답한다

Scenario: 동시 요청 충돌 방지
  Given 사용자가 thread_id "user-123"으로 요청을 보냈다
  And 해당 요청이 처리 중이다
  When 같은 thread_id로 새로운 요청이 들어온다
  Then 429 에러와 함께 CONCURRENT_REQUEST 코드를 반환한다
```

---

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|----|-------------|----------|--------------|
| FR-001 | `create_react_agent`를 사용하여 ReAct 에이전트 생성 | P0 (Must) | - |
| FR-002 | LLM 모델 설정 (Anthropic Claude) | P0 (Must) | FR-001 |
| FR-003 | Tool 등록 및 관리 시스템 | P0 (Must) | FR-001 |
| FR-004 | Middleware 체인 구조 설계 | P0 (Must) | - |
| FR-005 | 로깅 Middleware 구현 | P0 (Must) | FR-004 |
| FR-006 | 에러 핸들링 Middleware 구현 | P0 (Must) | FR-004 |
| FR-007 | 입력 검증 Middleware 구현 | P1 (Should) | FR-004 |
| FR-008 | 대화 상태 관리 (MemorySaver) | P0 (Must) | FR-001 |
| FR-009 | Thread 기반 대화 분리 | P0 (Must) | FR-008 |
| FR-010 | FastAPI 엔드포인트 구현 | P0 (Must) | FR-001, FR-004 |
| FR-011 | 스트리밍 응답 지원 (SSE) | P1 (Should) | FR-010 |
| FR-012 | Rate Limiting Middleware | P0 (Must) | FR-004 |
| FR-013 | Tool 실행 타임아웃 설정 | P1 (Should) | FR-003 |
| FR-014 | 커스텀 Tool 플러그인 인터페이스 | P1 (Should) | FR-003 |
| FR-015 | 세션 만료 및 정리 정책 | P0 (Must) | FR-008 |
| FR-016 | 동시 요청 충돌 처리 | P0 (Must) | FR-009 |
| FR-017 | LLM 폴백 및 재시도 로직 | P0 (Must) | FR-002 |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Metric | Target | Description |
|--------|--------|-------------|
| 응답 시간 (첫 토큰) | < 2s | 스트리밍 시 첫 토큰 도달 시간 |
| 전체 응답 시간 | < 30s | Tool 호출 포함 전체 응답 완료 |
| 동시 요청 처리 | 50+ | 동시 대화 세션 수 |
| 메모리 사용량 | < 1GB | 단일 인스턴스 기준 |
| Middleware 오버헤드 | < 50ms | Middleware 체인 실행 시간 |

### 4.2 Security

| Item | Requirement |
|------|-------------|
| API Key 관리 | 환경 변수로 관리, 코드에 하드코딩 금지 |
| 입력 검증 | 프롬프트 인젝션 방어 기본 검증 |
| 로깅 | 민감 정보 (API Key 등) 마스킹 |
| Rate Limiting | IP당 분당 60회, 전역 분당 1000회 |

### 4.3 Maintainability

| Item | Requirement |
|------|-------------|
| 코드 구조 | 레이어드 아키텍처 (Middleware → Agent → Tool) |
| 테스트 커버리지 | 핵심 로직 80% 이상 |
| 문서화 | 주요 함수/클래스 docstring 필수 |
| Python 버전 | >= 3.11 |

### 4.4 Memory Management

| Policy | Value | Description |
|--------|-------|-------------|
| Session TTL | 24시간 | 마지막 활동 후 자동 만료 |
| Max Sessions | 10,000 | 동시 활성 세션 최대 수 |
| Cleanup Interval | 1시간 | 만료 세션 정리 주기 |
| Message History Limit | 100 | 세션당 최대 메시지 수 |
| Max Context Tokens | 50,000 | 대화 히스토리 최대 토큰 (100k의 50%) |

**Persistence Strategy**:
- **개발 환경**: MemorySaver (In-Memory)
- **운영 환경**: PostgresSaver 또는 RedisSaver 권장

### 4.5 Logging Policy

| Level | Use Case |
|-------|----------|
| DEBUG | 개발 환경, 상세 디버깅 |
| INFO | 요청/응답 로깅, 주요 이벤트 |
| WARNING | 재시도, 폴백 발생 |
| ERROR | 처리된 예외 |
| CRITICAL | 서비스 중단 수준 오류 |

**Format**: JSON (운영), Console (개발)

---

## 5. Technical Design

### 5.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Middleware Chain (FastAPI Level)             │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │
│  │  │ Logging │→ │  Rate   │→ │Validate │→ │  Error  │     │   │
│  │  │   MW    │  │ Limit   │  │   MW    │  │Handler  │     │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Session Lock Manager                    │   │
│  │           (동시 요청 충돌 방지, thread_id별 락)            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              LangGraph ReAct Agent                        │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │           create_react_agent()                      │  │   │
│  │  │  ┌─────────┐    ┌─────────────┐    ┌──────────┐   │  │   │
│  │  │  │   LLM   │ ←→ │  StateGraph │ ←→ │  Tools   │   │  │   │
│  │  │  │(Claude) │    │   (ReAct)   │    │ Registry │   │  │   │
│  │  │  └─────────┘    └─────────────┘    └──────────┘   │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Memory Layer                            │   │
│  │  ┌────────────────┐    ┌────────────────────────────┐    │   │
│  │  │  MemorySaver   │    │  Session TTL Manager       │    │   │
│  │  │  (In-Memory)   │    │  (만료 세션 자동 정리)       │    │   │
│  │  └────────────────┘    └────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Middleware 통합 전략

**선택: FastAPI Middleware 레벨**

| 장점 | 설명 |
|------|------|
| 독립성 | LangGraph 내부 구현에 의존하지 않음 |
| 단순성 | before/after 패턴으로 충분한 제어 |
| 테스트 용이 | Middleware 독립 테스트 가능 |

```python
# Middleware 실행 순서
Request → Logging → RateLimit → Validation → Agent → ErrorHandler → Response
```

**Alternative (필요 시)**: LangGraph `callbacks` 파라미터로 Tool/LLM 호출 시점 개입

### 5.3 비동기 처리 전략

| Method | Use Case | LangGraph API |
|--------|----------|---------------|
| 일반 응답 | `stream=false` | `agent.ainvoke()` |
| 스트리밍 | `stream=true` | `agent.astream()` |

**필수**: 모든 Agent 호출은 비동기(`ainvoke`, `astream`) 사용

### 5.4 Directory Structure

```
wigtn-ai-agent/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 앱 엔트리포인트
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # 환경 설정
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── factory.py             # create_react_agent 래퍼
│   │   ├── prompts.py             # 시스템 프롬프트
│   │   ├── state.py               # 커스텀 State 정의
│   │   └── llm.py                 # LLM 설정 및 폴백 로직
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── base.py                # Middleware 베이스 클래스
│   │   ├── chain.py               # Middleware 체인 관리
│   │   ├── logging.py             # 로깅 Middleware
│   │   ├── error_handler.py       # 에러 핸들링 Middleware
│   │   ├── validation.py          # 입력 검증 Middleware
│   │   └── rate_limit.py          # Rate Limiting Middleware
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py            # Tool 레지스트리
│   │   ├── web_search.py          # 웹 검색 Tool 예시
│   │   └── calculator.py          # 계산기 Tool 예시
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── checkpointer.py        # 메모리/체크포인터 설정
│   │   ├── session_manager.py     # 세션 TTL 관리
│   │   └── lock_manager.py        # 동시 요청 락 관리
│   └── api/
│       ├── __init__.py
│       ├── routes.py              # API 라우트
│       └── schemas.py             # Pydantic 스키마
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_middleware.py
│   ├── test_tools.py
│   └── test_api.py
├── docs/
│   ├── prd/
│   └── todo_plan/
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

### 5.5 Core Components Design

#### 5.5.1 Agent Factory (`src/agent/factory.py`)

```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver

class AgentFactory:
    """ReAct Agent 생성 팩토리"""

    def __init__(
        self,
        llm: BaseChatModel,
        tools: list[BaseTool],
        checkpointer: BaseCheckpointSaver = None,
        system_prompt: str = None
    ):
        self.llm = llm
        self.tools = tools
        self.checkpointer = checkpointer or MemorySaver()
        self.system_prompt = system_prompt

    def create(self) -> CompiledGraph:
        """create_react_agent를 사용하여 에이전트 생성"""
        return create_react_agent(
            model=self.llm,
            tools=self.tools,
            checkpointer=self.checkpointer,
            state_modifier=self.system_prompt
        )
```

#### 5.5.2 LLM with Fallback (`src/agent/llm.py`)

```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnableWithFallbacks

class LLMFactory:
    """LLM 생성 및 폴백 설정"""

    @staticmethod
    def create_with_fallback() -> RunnableWithFallbacks:
        primary = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            max_retries=3,  # Exponential backoff: 1s, 2s, 4s
        )
        fallback = ChatOpenAI(
            model="gpt-4o-mini",
            max_retries=3,
        )
        return primary.with_fallbacks([fallback])
```

**재시도 정책**:
| 설정 | 값 |
|------|-----|
| 최대 재시도 | 3회 |
| Backoff | Exponential (1s, 2s, 4s) |
| 재시도 대상 | 429, 500, 502, 503, 504 |

**폴백 순서**:
| Priority | Model | Condition |
|----------|-------|-----------|
| 1 | claude-sonnet-4-20250514 | Default |
| 2 | gpt-4o-mini | Anthropic 장애 시 |

#### 5.5.3 Middleware Base (`src/middleware/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable
from dataclasses import dataclass, field

@dataclass
class MiddlewareContext:
    """Middleware 간 전달되는 컨텍스트"""
    request_id: str
    thread_id: str
    user_input: str
    metadata: dict = field(default_factory=dict)

@dataclass
class MiddlewareResult:
    """Middleware 처리 결과"""
    context: MiddlewareContext
    should_continue: bool = True
    response: Any = None
    error: Exception = None

class BaseMiddleware(ABC):
    """Middleware 추상 베이스 클래스"""

    @abstractmethod
    async def before(self, context: MiddlewareContext) -> MiddlewareResult:
        """에이전트 실행 전 처리"""
        pass

    @abstractmethod
    async def after(
        self,
        context: MiddlewareContext,
        response: Any
    ) -> MiddlewareResult:
        """에이전트 실행 후 처리"""
        pass

    @abstractmethod
    async def on_error(
        self,
        context: MiddlewareContext,
        error: Exception
    ) -> MiddlewareResult:
        """에러 발생 시 처리"""
        pass
```

#### 5.5.4 Session Lock Manager (`src/memory/lock_manager.py`)

```python
import asyncio
from typing import Dict

class SessionLockManager:
    """동시 요청 충돌 방지를 위한 세션별 락 관리"""

    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}
        self._lock_guard = asyncio.Lock()

    async def acquire(self, thread_id: str, timeout: float = 0) -> bool:
        """세션 락 획득 시도. timeout=0이면 즉시 반환"""
        async with self._lock_guard:
            if thread_id not in self._locks:
                self._locks[thread_id] = asyncio.Lock()

        lock = self._locks[thread_id]

        if timeout == 0:
            # 즉시 획득 시도 (대기 없음)
            return lock.locked() == False and await lock.acquire()
        else:
            try:
                return await asyncio.wait_for(lock.acquire(), timeout)
            except asyncio.TimeoutError:
                return False

    def release(self, thread_id: str) -> None:
        """세션 락 해제"""
        if thread_id in self._locks:
            self._locks[thread_id].release()
```

#### 5.5.5 Tool Registry (`src/tools/registry.py`)

```python
from langchain_core.tools import BaseTool
from typing import Dict, List

class ToolRegistry:
    """Tool 플러그인 레지스트리"""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Tool 등록"""
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        """Tool 해제"""
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> BaseTool | None:
        """Tool 조회"""
        return self._tools.get(name)

    def get_all(self) -> List[BaseTool]:
        """모든 Tool 목록"""
        return list(self._tools.values())

    def list_names(self) -> List[str]:
        """Tool 이름 목록"""
        return list(self._tools.keys())
```

**Tool 구현 방식**: LangChain의 `@tool` 데코레이터 또는 `BaseTool` 상속

```python
from langchain_core.tools import tool
from src.config.settings import settings

@tool
def web_search(query: str) -> str:
    """웹에서 정보를 검색합니다."""
    # 설정은 환경변수에서 주입
    api_key = settings.tavily_api_key
    # ... 구현
```

### 5.6 API Specification

#### 5.6.1 에러 코드 체계

**Naming Convention**: `{CATEGORY}_{SPECIFIC}`

| Category | Codes | Description |
|----------|-------|-------------|
| INPUT | `INVALID_INPUT`, `MESSAGE_TOO_LONG`, `MISSING_FIELD` | 입력 오류 |
| RATE | `RATE_LIMIT_EXCEEDED`, `CONCURRENT_REQUEST` | 요청 제한 |
| AGENT | `AGENT_ERROR`, `AGENT_TIMEOUT`, `MAX_ITERATIONS` | 에이전트 오류 |
| TOOL | `TOOL_ERROR`, `TOOL_TIMEOUT`, `TOOL_NOT_FOUND` | Tool 오류 |
| LLM | `LLM_ERROR`, `LLM_UNAVAILABLE`, `LLM_RATE_LIMIT` | LLM 오류 |
| SESSION | `SESSION_NOT_FOUND`, `SESSION_EXPIRED` | 세션 오류 |

#### 5.6.2 메시지 길이 정책

| Limit | Value | 근거 |
|-------|-------|------|
| Max Input | 4,000자 | Claude context의 약 10% |
| Max History | 50,000 토큰 | 100k context의 50% |

**토큰 추정**: 한글 1자 ≈ 2-3 토큰

#### 5.6.3 `POST /api/v1/chat`

**Description**: 챗봇에 메시지 전송 및 응답 수신

**Authentication**: None (추후 확장)

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| Content-Type | Yes | application/json |
| X-Request-ID | No | 요청 추적용 ID |

**Request Body**:
```json
{
  "message": "string (required) - 사용자 메시지, 최대 4,000자",
  "thread_id": "string (optional) - 대화 세션 ID, 미제공시 새 세션 생성",
  "stream": "boolean (optional) - 스트리밍 응답 여부, default: false"
}
```

**Request Example**:
```json
{
  "message": "오늘 서울 날씨 알려줘",
  "thread_id": "session-abc123",
  "stream": false
}
```

**Response 200 OK**:
```json
{
  "success": true,
  "data": {
    "response": "string - 에이전트 응답 메시지",
    "thread_id": "string - 대화 세션 ID",
    "tool_calls": [
      {
        "tool_name": "string - 호출된 Tool 이름",
        "tool_input": "object - Tool 입력값",
        "tool_output": "string - Tool 출력값"
      }
    ],
    "usage": {
      "prompt_tokens": "number - 입력 토큰 수",
      "completion_tokens": "number - 출력 토큰 수",
      "total_tokens": "number - 총 토큰 수"
    }
  },
  "meta": {
    "request_id": "string - 요청 ID",
    "timestamp": "string (ISO 8601) - 응답 시간",
    "latency_ms": "number - 처리 시간 (밀리초)"
  }
}
```

**Error Responses**:
| Status | Code | Message | Description |
|--------|------|---------|-------------|
| 400 | INVALID_INPUT | Invalid message format | 메시지 형식 오류 |
| 400 | MESSAGE_TOO_LONG | Message exceeds 4000 chars | 메시지 길이 초과 |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests | Rate limit 초과 |
| 429 | CONCURRENT_REQUEST | Another request in progress | 동일 세션 동시 요청 |
| 500 | AGENT_ERROR | Agent execution failed | 에이전트 실행 오류 |
| 500 | TOOL_ERROR | Tool execution failed | Tool 실행 오류 |
| 503 | LLM_UNAVAILABLE | LLM service unavailable | LLM 서비스 불가 |

**Error Response Format**:
```json
{
  "success": false,
  "error": {
    "code": "AGENT_ERROR",
    "message": "Agent execution failed",
    "details": {
      "reason": "Tool timeout",
      "tool_name": "web_search"
    }
  },
  "meta": {
    "request_id": "req-xyz789",
    "timestamp": "2026-01-18T10:30:00Z"
  }
}
```

**Rate Limiting**:
| Scope | Limit | Window |
|-------|-------|--------|
| IP별 | 60 req | 1분 |
| 전역 | 1000 req | 1분 |

#### 5.6.4 `POST /api/v1/chat` (Streaming)

**Description**: SSE 스트리밍 응답

**Request**: `stream: true` 설정

**Event Types**:
| Event | Description |
|-------|-------------|
| `start` | 응답 시작 |
| `token` | 텍스트 토큰 |
| `tool_call` | Tool 호출 시작 |
| `tool_result` | Tool 결과 |
| `end` | 응답 완료 |
| `error` | 에러 발생 |

**Chunk Format**:
```
event: start
data: {"thread_id": "abc123", "request_id": "req-xyz"}

event: token
data: {"content": "안녕", "index": 0}

event: token
data: {"content": "하세요", "index": 1}

event: tool_call
data: {"tool": "web_search", "input": {"query": "서울 날씨"}}

event: tool_result
data: {"tool": "web_search", "output": "서울 날씨: 맑음, 15°C"}

event: token
data: {"content": "현재 서울은", "index": 2}

event: end
data: {"usage": {"total_tokens": 150}, "latency_ms": 1250}
```

#### 5.6.5 `GET /api/v1/chat/{thread_id}/history`

**Description**: 특정 세션의 대화 히스토리 조회

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| thread_id | string | 대화 세션 ID |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | number | 50 | 조회할 메시지 수 (max: 100) |
| offset | number | 0 | 시작 위치 |

**Response 200 OK**:
```json
{
  "success": true,
  "data": {
    "thread_id": "session-abc123",
    "messages": [
      {
        "role": "user",
        "content": "안녕",
        "timestamp": "2026-01-18T10:00:00Z"
      },
      {
        "role": "assistant",
        "content": "안녕하세요! 무엇을 도와드릴까요?",
        "timestamp": "2026-01-18T10:00:02Z",
        "tool_calls": []
      }
    ],
    "total_count": 10
  }
}
```

**Error Responses**:
| Status | Code | Message |
|--------|------|---------|
| 404 | SESSION_NOT_FOUND | Session not found |
| 410 | SESSION_EXPIRED | Session has expired |

#### 5.6.6 `DELETE /api/v1/chat/{thread_id}`

**Description**: 특정 세션 삭제

**Response 200 OK**:
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "thread_id": "session-abc123"
  }
}
```

#### 5.6.7 `GET /api/v1/tools`

**Description**: 등록된 Tool 목록 조회

**Response 200 OK**:
```json
{
  "success": true,
  "data": {
    "tools": [
      {
        "name": "web_search",
        "description": "웹에서 정보를 검색합니다",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "검색 쿼리"
            }
          },
          "required": ["query"]
        }
      }
    ],
    "total_count": 5
  }
}
```

#### 5.6.8 `GET /api/v1/health`

**Description**: 서비스 상태 확인

**Response 200 OK**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "checks": {
      "memory": "available",
      "tools_registered": 5
    }
  }
}
```

**참고**: LLM 실제 호출은 비용 발생으로 헬스체크에서 제외. API Key 유효성만 환경변수 존재 여부로 확인.

---

## 6. Implementation Phases

### Phase 1: 프로젝트 기초 설정
- [ ] 프로젝트 구조 생성
- [ ] pyproject.toml / requirements.txt 작성
- [ ] 환경 설정 모듈 구현 (src/config/settings.py)
- [ ] .env.example 작성

**Deliverable**: 실행 가능한 빈 프로젝트 구조

### Phase 2: LangGraph Agent 핵심 구현
- [ ] LLM 연결 설정 (ChatAnthropic + 폴백)
- [ ] AgentFactory 클래스 구현
- [ ] create_react_agent 래퍼 구현
- [ ] MemorySaver 연동
- [ ] 기본 시스템 프롬프트 작성

**Deliverable**: 동작하는 ReAct Agent

### Phase 3: Middleware 시스템 구현
- [ ] BaseMiddleware 추상 클래스 정의
- [ ] MiddlewareChain 관리자 구현
- [ ] LoggingMiddleware 구현
- [ ] ErrorHandlerMiddleware 구현
- [ ] ValidationMiddleware 구현
- [ ] RateLimitMiddleware 구현

**Deliverable**: 완전한 Middleware 체인 시스템

### Phase 4: Tool 시스템 구현
- [ ] Tool 레지스트리 구현
- [ ] 예시 Tool 구현 (웹 검색, 계산기)
- [ ] Tool 타임아웃 처리

**Deliverable**: 확장 가능한 Tool 플러그인 시스템

### Phase 5: 메모리 및 세션 관리
- [ ] SessionManager 구현 (TTL 관리)
- [ ] SessionLockManager 구현 (동시 요청 방지)
- [ ] 세션 정리 백그라운드 태스크

**Deliverable**: 안정적인 세션 관리 시스템

### Phase 6: API 서버 구현
- [ ] FastAPI 앱 설정
- [ ] /chat 엔드포인트 구현
- [ ] /chat/{thread_id}/history 엔드포인트 구현
- [ ] /chat/{thread_id} DELETE 엔드포인트 구현
- [ ] /tools 엔드포인트 구현
- [ ] /health 엔드포인트 구현
- [ ] Pydantic 스키마 정의
- [ ] 스트리밍 응답 구현 (SSE)

**Deliverable**: 완전한 REST API 서버

### Phase 7: 테스트 및 문서화
- [ ] Agent 단위 테스트 작성
- [ ] Middleware 단위 테스트 작성
- [ ] Tool 단위 테스트 작성
- [ ] API 통합 테스트 작성
- [ ] README.md 작성

**Deliverable**: 테스트 완료된 프로젝트

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Agent 응답 성공률 | > 95% | 성공 응답 수 / 전체 요청 수 |
| 평균 응답 시간 | < 5s | Tool 호출 포함 전체 응답 |
| Middleware 처리 오버헤드 | < 50ms | Middleware 체인 실행 시간 |
| 테스트 커버리지 | > 80% | pytest-cov 측정 |
| Tool 호출 정확도 | > 90% | 적절한 Tool 선택 비율 |
| 세션 메모리 효율 | < 10MB/session | 세션당 평균 메모리 |

---

## 8. Dependencies

### Python Packages

```
# Core
langgraph>=0.2.0
langchain>=0.3.0
langchain-anthropic>=0.3.0
langchain-openai>=0.2.0

# API
fastapi>=0.115.0
uvicorn>=0.32.0
sse-starlette>=2.0.0

# Validation & Config
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0

# Logging
structlog>=24.0.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.24.0
pytest-cov>=5.0.0
httpx>=0.27.0
```

**Python Version**: >= 3.11

### External Services

| Service | Purpose | Required |
|---------|---------|----------|
| Anthropic API | LLM (Claude) - Primary | Yes |
| OpenAI API | LLM (GPT) - Fallback | No |
| Tavily API | 웹 검색 Tool | Optional |

---

## 9. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM API 장애 | High | Low | 폴백 모델(GPT-4o-mini), 재시도 로직(3회, exponential backoff) |
| Tool 타임아웃 | Medium | Medium | 타임아웃 설정(30s), 사용자 알림, graceful 에러 처리 |
| 메모리 누수 | High | Medium | 세션 TTL(24h), 최대 세션 수 제한(10,000), 주기적 정리 |
| 프롬프트 인젝션 | High | Medium | 입력 검증 Middleware, 시스템 프롬프트 보호 |
| 동시 요청 충돌 | Medium | Medium | 세션별 락 메커니즘 |
| LLM 비용 폭증 | High | Medium | Rate Limiting (IP당 60req/min) |

---

## 10. Glossary

| Term | Definition |
|------|------------|
| ReAct | Reasoning + Acting 패턴, LLM이 추론과 행동을 반복 |
| Tool | 에이전트가 외부 작업을 수행하기 위해 호출하는 함수 |
| Middleware | 요청/응답 처리 파이프라인의 중간 처리 레이어 |
| Checkpointer | 대화 상태를 저장/복원하는 컴포넌트 |
| Thread | 독립적인 대화 세션 단위 |
| SSE | Server-Sent Events, 서버에서 클라이언트로 단방향 스트리밍 |
| TTL | Time To Live, 데이터 만료 시간 |
