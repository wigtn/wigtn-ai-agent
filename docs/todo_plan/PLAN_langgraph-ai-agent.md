# Task Plan: LangGraph AI Agent Chatbot

> **Generated from**: docs/prd/PRD_langgraph-ai-agent.md
> **Created**: 2026-01-18
> **Updated**: 2026-01-18 (PRD Review 반영)
> **Status**: pending

## Execution Config

| Option | Value | Description |
|--------|-------|-------------|
| `auto_commit` | true | 완료 시 자동 커밋 |
| `commit_per_phase` | true | Phase별 중간 커밋 |
| `quality_gate` | true | /auto-commit 품질 검사 |

---

## Phases

### Phase 1: 프로젝트 기초 설정

**목표**: 실행 가능한 빈 프로젝트 구조 생성

| Task ID | Task | Priority | Dependencies | Status |
|---------|------|----------|--------------|--------|
| T1-001 | 프로젝트 디렉토리 구조 생성 | P0 | - | [ ] |
| T1-002 | pyproject.toml 작성 (의존성, 메타데이터) | P0 | T1-001 | [ ] |
| T1-003 | requirements.txt 작성 | P0 | T1-001 | [ ] |
| T1-004 | src/config/settings.py 환경 설정 모듈 구현 | P0 | T1-002 | [ ] |
| T1-005 | .env.example 작성 | P0 | T1-004 | [ ] |
| T1-006 | 각 모듈 __init__.py 파일 생성 | P0 | T1-001 | [ ] |

**Deliverable**: 실행 가능한 빈 프로젝트 구조

---

### Phase 2: LangGraph Agent 핵심 구현

**목표**: 동작하는 ReAct Agent 구축 (폴백 포함)

| Task ID | Task | Priority | Dependencies | Status |
|---------|------|----------|--------------|--------|
| T2-001 | src/agent/state.py - 커스텀 State 정의 | P0 | Phase 1 | [ ] |
| T2-002 | src/agent/prompts.py - 시스템 프롬프트 작성 | P0 | Phase 1 | [ ] |
| T2-003 | src/agent/llm.py - LLM 설정 및 폴백 로직 구현 | P0 | Phase 1 | [ ] |
| T2-004 | src/memory/checkpointer.py - MemorySaver 설정 | P0 | Phase 1 | [ ] |
| T2-005 | src/agent/factory.py - AgentFactory 클래스 구현 | P0 | T2-001, T2-002, T2-003, T2-004 | [ ] |
| T2-006 | create_react_agent 통합 및 기본 테스트 | P0 | T2-005 | [ ] |

**Deliverable**: 동작하는 ReAct Agent (폴백 포함)

---

### Phase 3: Middleware 시스템 구현

**목표**: 완전한 Middleware 체인 시스템 구축

| Task ID | Task | Priority | Dependencies | Status |
|---------|------|----------|--------------|--------|
| T3-001 | src/middleware/base.py - BaseMiddleware 추상 클래스 정의 | P0 | Phase 1 | [ ] |
| T3-002 | src/middleware/chain.py - MiddlewareChain 관리자 구현 | P0 | T3-001 | [ ] |
| T3-003 | src/middleware/logging.py - LoggingMiddleware 구현 | P0 | T3-001 | [ ] |
| T3-004 | src/middleware/error_handler.py - ErrorHandlerMiddleware 구현 | P0 | T3-001 | [ ] |
| T3-005 | src/middleware/validation.py - ValidationMiddleware 구현 | P1 | T3-001 | [ ] |
| T3-006 | src/middleware/rate_limit.py - RateLimitMiddleware 구현 | P0 | T3-001 | [ ] |
| T3-007 | Middleware 체인 통합 테스트 | P0 | T3-002, T3-003, T3-004, T3-006 | [ ] |

**Deliverable**: 완전한 Middleware 체인 시스템

---

### Phase 4: Tool 시스템 구현

**목표**: 확장 가능한 Tool 플러그인 시스템 구축

| Task ID | Task | Priority | Dependencies | Status |
|---------|------|----------|--------------|--------|
| T4-001 | src/tools/registry.py - Tool 레지스트리 구현 | P0 | Phase 1 | [ ] |
| T4-002 | src/tools/web_search.py - 웹 검색 Tool 구현 | P1 | T4-001 | [ ] |
| T4-003 | src/tools/calculator.py - 계산기 Tool 구현 | P1 | T4-001 | [ ] |
| T4-004 | Tool 타임아웃 처리 로직 추가 (30s) | P1 | T4-001 | [ ] |
| T4-005 | Agent와 Tool 통합 테스트 | P0 | T4-001, Phase 2 | [ ] |

**Deliverable**: 확장 가능한 Tool 플러그인 시스템

---

### Phase 5: 메모리 및 세션 관리

**목표**: 안정적인 세션 관리 시스템 구축

| Task ID | Task | Priority | Dependencies | Status |
|---------|------|----------|--------------|--------|
| T5-001 | src/memory/session_manager.py - SessionManager 구현 (TTL 관리) | P0 | Phase 1 | [ ] |
| T5-002 | src/memory/lock_manager.py - SessionLockManager 구현 | P0 | Phase 1 | [ ] |
| T5-003 | 세션 정리 백그라운드 태스크 구현 (1시간 주기) | P0 | T5-001 | [ ] |
| T5-004 | 최대 세션 수 제한 로직 (10,000) | P0 | T5-001 | [ ] |
| T5-005 | 메시지 히스토리 제한 로직 (100개) | P1 | T5-001 | [ ] |
| T5-006 | 세션 관리 통합 테스트 | P0 | T5-001, T5-002, T5-003 | [ ] |

**Deliverable**: 안정적인 세션 관리 시스템

---

### Phase 6: API 서버 구현

**목표**: 완전한 REST API 서버 구축

| Task ID | Task | Priority | Dependencies | Status |
|---------|------|----------|--------------|--------|
| T6-001 | src/api/schemas.py - Pydantic 스키마 정의 | P0 | Phase 1 | [ ] |
| T6-002 | src/main.py - FastAPI 앱 설정 | P0 | T6-001 | [ ] |
| T6-003 | src/api/routes.py - POST /chat 엔드포인트 구현 | P0 | T6-002, Phase 2, Phase 3, Phase 5 | [ ] |
| T6-004 | src/api/routes.py - GET /chat/{thread_id}/history 엔드포인트 구현 | P0 | T6-003 | [ ] |
| T6-005 | src/api/routes.py - DELETE /chat/{thread_id} 엔드포인트 구현 | P1 | T6-003 | [ ] |
| T6-006 | src/api/routes.py - GET /tools 엔드포인트 구현 | P1 | T6-002, Phase 4 | [ ] |
| T6-007 | src/api/routes.py - GET /health 엔드포인트 구현 | P0 | T6-002 | [ ] |
| T6-008 | SSE 스트리밍 응답 구현 (astream 사용) | P1 | T6-003 | [ ] |
| T6-009 | 에러 코드 체계 구현 (INPUT, RATE, AGENT, TOOL, LLM, SESSION) | P0 | T6-001 | [ ] |
| T6-010 | API 통합 테스트 | P0 | T6-003, T6-004 | [ ] |

**Deliverable**: 완전한 REST API 서버

---

### Phase 7: 테스트 및 문서화

**목표**: 테스트 완료된 프로젝트

| Task ID | Task | Priority | Dependencies | Status |
|---------|------|----------|--------------|--------|
| T7-001 | tests/test_agent.py - Agent 단위 테스트 작성 | P0 | Phase 2 | [ ] |
| T7-002 | tests/test_middleware.py - Middleware 단위 테스트 작성 | P0 | Phase 3 | [ ] |
| T7-003 | tests/test_tools.py - Tool 단위 테스트 작성 | P0 | Phase 4 | [ ] |
| T7-004 | tests/test_session.py - 세션 관리 테스트 작성 | P0 | Phase 5 | [ ] |
| T7-005 | tests/test_api.py - API 통합 테스트 작성 | P0 | Phase 6 | [ ] |
| T7-006 | README.md 작성 | P1 | All Phases | [ ] |
| T7-007 | 테스트 커버리지 80% 달성 확인 | P0 | T7-001 ~ T7-005 | [ ] |

**Deliverable**: 테스트 완료된 프로젝트

---

## Progress

| Metric | Value |
|--------|-------|
| Total Tasks | 0/42 |
| Current Phase | Phase 1 |
| Status | pending |

## Phase Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| Phase 1: 프로젝트 기초 설정 | 0/6 | pending |
| Phase 2: LangGraph Agent 핵심 구현 | 0/6 | pending |
| Phase 3: Middleware 시스템 구현 | 0/7 | pending |
| Phase 4: Tool 시스템 구현 | 0/5 | pending |
| Phase 5: 메모리 및 세션 관리 | 0/6 | pending |
| Phase 6: API 서버 구현 | 0/10 | pending |
| Phase 7: 테스트 및 문서화 | 0/7 | pending |

---

## Execution Log

| Timestamp | Phase | Task | Status | Notes |
|-----------|-------|------|--------|-------|
| - | - | - | - | - |

---

## Notes

### 의존성 관계
```
Phase 1 (기초 설정)
    ↓
    ├── Phase 2 (Agent) ─────┐
    ├── Phase 3 (Middleware) ├── Phase 6 (API)
    ├── Phase 4 (Tools) ─────┤      ↓
    └── Phase 5 (Session) ───┘   Phase 7 (Test)
```

- Phase 2, 3, 4, 5는 Phase 1 완료 후 **병렬** 진행 가능
- Phase 6은 Phase 2, 3, 5 완료 필요 (Phase 4는 부분적으로 필요)
- Phase 7은 각 Phase 완료 시점에 해당 테스트 작성 가능

### 우선순위 가이드
- **P0**: 반드시 구현 (MVP 필수) - 17개 요구사항
- **P1**: 가능하면 구현 (기능 완성도)
- **P2**: 있으면 좋음 (추후 추가 가능)

### 커밋 전략
- `commit_per_phase: true` 설정으로 각 Phase 완료 시 커밋
- 커밋 메시지 형식: `feat(phase-N): [Phase 설명]`

### 주요 변경사항 (v1.1)
1. **FR-012 Rate Limiting**: P2 → P0 상향
2. **FR-015 세션 만료 정책**: 신규 추가 (P0)
3. **FR-016 동시 요청 충돌 처리**: 신규 추가 (P0)
4. **FR-017 LLM 폴백/재시도**: 신규 추가 (P0)
5. **Phase 5 추가**: 메모리 및 세션 관리 (기존 6단계 → 7단계)
6. **스트리밍 API 상세화**: SSE 이벤트 형식 정의
7. **에러 코드 체계**: 6개 카테고리로 표준화
