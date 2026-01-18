# PRD Analysis Report

## 분석 대상
- **문서**: `docs/prd/PRD_langgraph-ai-agent.md`
- **버전**: 1.0
- **분석일**: 2026-01-18

---

## 요약

| 카테고리 | 발견 | Critical | Major | Minor |
|----------|------|----------|-------|-------|
| 완전성 | 7 | 2 | 3 | 2 |
| 실현가능성 | 5 | 1 | 3 | 1 |
| 보안 | 4 | 1 | 2 | 1 |
| 일관성 | 3 | 0 | 2 | 1 |
| **총계** | **19** | **4** | **10** | **5** |

---

## 상세 분석

### 🔴 Critical (즉시 수정 필요)

#### C-1. 세션 만료/정리 정책 미정의
- **위치**: Section 5.3 - Memory Layer, FR-008
- **문제**: MemorySaver 사용 시 세션 TTL, 정리 정책이 없음. In-Memory 저장소는 서버 재시작 시 모든 대화 데이터 유실
- **영향**:
  - 메모리 누수로 서버 OOM 발생 가능
  - 장기 운영 시 메모리 사용량 지속 증가
  - 서버 재시작 시 모든 사용자 대화 히스토리 유실
- **개선안**:
  ```markdown
  ### 4.4 Memory Management

  | Policy | Value | Description |
  |--------|-------|-------------|
  | Session TTL | 24시간 | 마지막 활동 후 자동 만료 |
  | Max Sessions | 10,000 | 동시 활성 세션 최대 수 |
  | Cleanup Interval | 1시간 | 만료 세션 정리 주기 |
  | Message History Limit | 100 | 세션당 최대 메시지 수 |

  ### Persistence Strategy (선택)
  - **개발 환경**: MemorySaver (In-Memory)
  - **운영 환경**: PostgresSaver 또는 RedisSaver 권장
  ```

#### C-2. LangGraph Middleware 연동 방식 불명확
- **위치**: Section 5.1 Architecture, Section 5.3.2
- **문제**: `create_react_agent`는 내부적으로 완전한 StateGraph를 생성함. PRD의 커스텀 Middleware Chain이 LangGraph의 실행 흐름과 어떻게 통합되는지 불명확
- **영향**:
  - 구현 시 아키텍처 혼란 발생
  - Middleware가 Agent 내부 상태에 접근 불가할 수 있음
  - 스트리밍 중간에 Middleware 개입 불가능
- **개선안**:
  ```markdown
  ### 5.3.4 Middleware 통합 전략

  **Option A: FastAPI 미들웨어 레벨** (권장)
  - FastAPI의 Middleware/Dependency로 구현
  - Agent 호출 전/후에만 개입
  - LangGraph 내부 상태와 독립적

  **Option B: LangGraph Callback 활용**
  - LangGraph의 `callbacks` 파라미터 활용
  - Tool 호출, LLM 호출 시점에 개입 가능
  - 더 세밀한 제어 가능

  **선택**: Option A (FastAPI 레벨)
  - 이유: LangGraph 내부 구현에 의존하지 않음
  - before/after 패턴으로 충분한 제어 가능
  ```

#### C-3. 비동기 처리 전략 미정의
- **위치**: Section 5.3.1 Agent Factory, Section 5.4 API
- **문제**: FastAPI는 async 기반인데, LangGraph agent의 `invoke` vs `ainvoke` 사용이 명시되지 않음. 스트리밍 시 `astream` 사용 여부 불명확
- **영향**:
  - 동기 호출 시 이벤트 루프 블로킹
  - 동시 요청 처리 성능 저하
  - 스트리밍 구현 방향 불명확
- **개선안**:
  ```markdown
  ### 5.3.5 비동기 처리 전략

  | Method | Use Case | LangGraph API |
  |--------|----------|---------------|
  | 일반 응답 | stream=false | `agent.ainvoke()` |
  | 스트리밍 | stream=true | `agent.astream()` |

  **필수**: 모든 Agent 호출은 비동기(`ainvoke`, `astream`) 사용
  ```

#### C-4. Rate Limiting이 P2이지만 보안상 필수
- **위치**: FR-012, Section 4.2 Security
- **문제**: Rate Limiting이 P2 (Could Have)로 분류되어 있으나, API 남용/DDoS 방어를 위해 필수임
- **영향**:
  - API 남용으로 LLM API 비용 폭증
  - 서비스 가용성 저하
  - 특정 사용자의 리소스 독점
- **개선안**:
  ```markdown
  FR-012 우선순위 변경: P2 → P0

  Rate Limiting 정책 추가:
  | Endpoint | Limit | Window |
  |----------|-------|--------|
  | POST /chat | 60 req | 1분 |
  | GET /history | 100 req | 1분 |
  | Global | 1000 req | 1분 |
  ```

---

### 🟡 Major (구현 전 수정 권장)

#### M-1. 스트리밍 API 상세 미정의
- **위치**: Section 5.4 - POST /api/v1/chat
- **문제**: `stream=true` 시 SSE 응답 형식, 이벤트 타입, chunk 구조가 정의되지 않음
- **개선안**:
  ```markdown
  ### 스트리밍 응답 (SSE)

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
  ```json
  event: token
  data: {"content": "안녕", "index": 0}

  event: tool_call
  data: {"tool": "web_search", "input": {"query": "날씨"}}

  event: end
  data: {"usage": {"total_tokens": 150}, "thread_id": "abc"}
  ```

#### M-2. 동시 요청 충돌 처리 미정의
- **위치**: FR-009 Thread 기반 대화 분리
- **문제**: 같은 thread_id로 동시에 여러 요청이 들어올 때 처리 방식 미정의
- **개선안**:
  ```markdown
  ### 동시 요청 처리 정책

  **전략**: 세션별 락 (Pessimistic Locking)
  - 같은 thread_id로 동시 요청 시 두 번째 요청은 429 반환
  - Error Code: `CONCURRENT_REQUEST`
  - Message: "Another request is in progress for this session"
  ```

#### M-3. LLM 폴백/재시도 전략 상세 미정의
- **위치**: Section 9 Risks and Mitigations
- **문제**: "폴백 모델 설정, 재시도 로직" 언급만 있고 구체적 전략 없음
- **개선안**:
  ```markdown
  ### LLM 폴백 전략

  **재시도 정책**:
  - 최대 재시도: 3회
  - Backoff: Exponential (1s, 2s, 4s)
  - 재시도 대상: 429, 500, 502, 503, 504

  **폴백 모델**:
  | Priority | Model | Condition |
  |----------|-------|-----------|
  | 1 | claude-3-5-sonnet | Default |
  | 2 | claude-3-haiku | Sonnet 장애 시 |
  | 3 | gpt-4o-mini | Anthropic 전체 장애 시 |
  ```

#### M-4. 아키텍처 다이어그램 Auth MW 모순
- **위치**: Section 5.1 Architecture Overview
- **문제**: 아키텍처에 "Auth MW"가 포함되어 있으나, Non-Goals에서 "사용자 인증/인가 시스템 (별도 PRD로 분리)"로 명시
- **개선안**:
  - 아키텍처 다이어그램에서 Auth MW 제거
  - 또는 "Placeholder for future Auth MW" 주석 추가

#### M-5. Tool 플러그인 인터페이스 상세 미흡
- **위치**: FR-014, Section 5.3
- **문제**:
  - BaseTool이 LangChain의 BaseTool과 어떤 관계인지 불명확
  - Tool 동적 등록/해제 메커니즘 없음
  - Tool 설정(API Key 등) 주입 방식 미정의
- **개선안**:
  ```markdown
  ### Tool 플러그인 인터페이스

  **BaseTool 관계**:
  - LangChain의 `BaseTool` 또는 `@tool` 데코레이터 직접 사용
  - 별도 래퍼 불필요

  **Tool 등록 방식**:
  ```python
  # tools/registry.py
  class ToolRegistry:
      def register(self, tool: BaseTool) -> None: ...
      def unregister(self, name: str) -> None: ...
      def get_all(self) -> list[BaseTool]: ...

  # 설정 주입
  @tool
  def web_search(query: str) -> str:
      api_key = settings.tavily_api_key  # 환경변수에서
      ...
  ```

#### M-6. 에러 코드 체계 불완전
- **위치**: Section 5.4 Error Responses
- **문제**: Tool별 에러 코드, 에러 코드 네이밍 컨벤션이 불명확
- **개선안**:
  ```markdown
  ### 에러 코드 체계

  **Naming Convention**: `{CATEGORY}_{SPECIFIC}`

  | Category | Codes |
  |----------|-------|
  | INPUT | INVALID_INPUT, MESSAGE_TOO_LONG, MISSING_FIELD |
  | AUTH | UNAUTHORIZED, FORBIDDEN, TOKEN_EXPIRED |
  | RATE | RATE_LIMIT_EXCEEDED, CONCURRENT_REQUEST |
  | AGENT | AGENT_ERROR, AGENT_TIMEOUT, MAX_ITERATIONS |
  | TOOL | TOOL_ERROR, TOOL_TIMEOUT, TOOL_NOT_FOUND |
  | LLM | LLM_ERROR, LLM_UNAVAILABLE, LLM_RATE_LIMIT |
  ```

#### M-7. 메시지 길이 제한 근거 없음
- **위치**: Section 5.4 - MESSAGE_TOO_LONG (10,000자)
- **문제**: 10,000자 제한의 근거가 없음. LLM 컨텍스트 윈도우 고려 필요
- **개선안**:
  ```markdown
  ### 메시지 길이 정책

  | Limit | Value | 근거 |
  |-------|-------|------|
  | Max Input | 4,000자 | Claude context의 약 10% |
  | Max History | 50,000 토큰 | 100k context의 50% |

  **토큰 추정**: 한글 1자 ≈ 2-3 토큰
  ```

---

### 🟢 Minor (개선 제안)

#### m-1. Python 버전 미명시
- **위치**: Section 8 Dependencies
- **문제**: Python 버전 요구사항이 없음
- **개선안**: `Python >= 3.11` 명시 (LangGraph 요구사항 기준)

#### m-2. 용어 불일치
- **위치**: 전체 문서
- **문제**:
  - "Middleware" / "미들웨어" 혼용
  - "Tool" / "도구" 혼용
- **개선안**: 영문 용어로 통일 (Middleware, Tool)

#### m-3. 테스트 파일 구조 불완전
- **위치**: Section 5.2 Directory Structure
- **문제**: `test_api.py`가 디렉토리 구조에 없음
- **개선안**: `tests/test_api.py` 추가

#### m-4. 로깅 레벨/포맷 미정의
- **위치**: FR-005, Section 4.3
- **문제**: structlog 사용 언급만 있고 로깅 레벨, 포맷 등 상세 없음
- **개선안**:
  ```markdown
  ### 로깅 정책

  | Level | Use Case |
  |-------|----------|
  | DEBUG | 개발 환경, 상세 디버깅 |
  | INFO | 요청/응답 로깅, 주요 이벤트 |
  | WARNING | 재시도, 폴백 발생 |
  | ERROR | 처리된 예외 |
  | CRITICAL | 서비스 중단 수준 오류 |

  **Format**: JSON (운영), Console (개발)
  ```

#### m-5. 헬스체크 상세 미흡
- **위치**: Section 5.4 - GET /health
- **문제**: `llm_status: "connected"` 판단 기준이 불명확
- **개선안**:
  ```markdown
  ### 헬스체크 상세

  | Check | Method | Timeout |
  |-------|--------|---------|
  | llm_status | API Key 유효성만 검증 (호출 X) | - |
  | memory_status | Checkpointer 연결 확인 | 1s |

  **참고**: 실제 LLM 호출은 비용 발생으로 제외
  ```

---

## 누락된 요구사항

| ID | 요구사항 | 권장 우선순위 | 설명 |
|----|---------|--------------|------|
| NEW-1 | 세션 TTL 및 만료 정책 | P0 | 메모리 관리 필수 |
| NEW-2 | 동시 요청 충돌 처리 | P0 | 데이터 정합성 |
| NEW-3 | 스트리밍 응답 상세 스펙 | P1 | SSE 이벤트 형식 |
| NEW-4 | LLM 재시도/폴백 상세 전략 | P1 | 안정성 확보 |
| NEW-5 | 메시지 히스토리 최대 보관 수 | P1 | 메모리/컨텍스트 관리 |
| NEW-6 | Graceful Shutdown 처리 | P2 | 진행 중 요청 완료 보장 |
| NEW-7 | Tool 결과 캐싱 전략 | P2 | 동일 쿼리 최적화 |

---

## 리스크 매트릭스 (추가)

| 리스크 | 발생 확률 | 영향도 | 대응 방안 |
|--------|----------|--------|----------|
| 세션 메모리 폭증 | 높음 | 높음 | TTL + 최대 세션 수 제한 |
| 동시 요청 데이터 충돌 | 중 | 높음 | 세션별 락 메커니즘 |
| LLM 비용 폭증 | 중 | 높음 | Rate Limiting 필수 적용 |
| 스트리밍 연결 끊김 | 중 | 중 | 재연결 로직, 부분 응답 처리 |
| Tool 무한 루프 | 낮음 | 높음 | max_iterations 설정 |

---

## 권장 조치

### 즉시 조치 (Critical) - 구현 전 필수
1. ❗ 세션 만료/정리 정책 추가 (C-1)
2. ❗ Middleware 통합 전략 명확화 (C-2)
3. ❗ 비동기 처리 전략 정의 (C-3)
4. ❗ Rate Limiting P0으로 상향 (C-4)

### 구현 전 조치 (Major)
1. ⚠️ 스트리밍 API 상세 정의 (M-1)
2. ⚠️ 동시 요청 충돌 처리 정의 (M-2)
3. ⚠️ LLM 폴백/재시도 전략 상세화 (M-3)
4. ⚠️ 아키텍처 다이어그램 Auth MW 정리 (M-4)
5. ⚠️ Tool 플러그인 인터페이스 상세화 (M-5)
6. ⚠️ 에러 코드 체계 정립 (M-6)
7. ⚠️ 메시지 길이 제한 근거 추가 (M-7)

### 가능하면 조치 (Minor)
1. 💡 Python 버전 명시 (m-1)
2. 💡 용어 통일 (m-2)
3. 💡 test_api.py 추가 (m-3)
4. 💡 로깅 정책 상세화 (m-4)
5. 💡 헬스체크 상세화 (m-5)

---

## 다음 단계

```
┌─────────────────────────────────────────────────────────────┐
│  ✅ PRD 분석 완료                                            │
│                                                             │
│  권장 액션:                                                  │
│  1. Critical 이슈 4개를 PRD에 반영                           │
│  2. Major 이슈 중 M-1 ~ M-3 우선 반영                        │
│  3. 수정 완료 후 `/implement langgraph-ai-agent` 실행        │
│                                                             │
│  💡 Critical 이슈가 모두 해결되면 구현을 시작해도 좋습니다.    │
│     Major 이슈는 구현 중 병행 수정 가능합니다.                │
└─────────────────────────────────────────────────────────────┘
```

**PRD 수정을 원하시면**: "PRD 수정해줘" 또는 "Critical 이슈 반영해줘"
**바로 구현을 시작하려면**: `/implement langgraph-ai-agent`
