# KEEP Plans

Created: 2026-06-04

## Setup

```bash
uv sync --dev               # install dev dependencies (pytest)
uv run pytest -q            # run tests
```

---

## Phase 1: Wire the real AgentDojo benchmark

| Task | Content | DoD | Depends | Status |
|------|---------|-----|---------|--------|
| 1.1  | Add `pyproject.toml` (src layout) for `pip install -e .` | `uv sync --dev` completes without error | - | cc:done [e44dc80] |
| 1.2  | Pin AgentDojo as dependency; record exact version | Version pinned in pyproject.toml | 1.1 | cc:done [8e8f09f] |
| 1.3  | Identify and document banking-suite scenario(s) by ID in `THREAT.md` | Scenario IDs documented and linked | 1.2 | cc:done [ab68fcb] |
| 1.4  | Adapter: AgentDojo user task → KEEP deriver input | Adapter converts user task to trusted instruction | 1.3 | cc:done [4e66a98] |
| 1.5  | Adapter: AgentDojo tool schema → KEEP capability scope | Adapter generates capabilities for all AgentDojo tools | 1.4 | cc:done [5201b89] |
| 1.6  | Route every AgentDojo tool call through `TrustedBase.authorize` | All calls intercepted; audit log recorded | 1.5 | cc:done [d164c05] |
| 1.7  | Reproduce one documented banking injection end-to-end | Injection scenario runs against real environment | 1.6 | cc:done [2e7a6a8] |
| 1.8  | Test: real-scenario injection blocked by base | `uv run pytest` passes; injection blocked; logs show decision | 1.7 | cc:done [2e7a6a8] |
| 1.9  | Handle multi-step tasks: capability lifecycle across episode | Capabilities expire/renew correctly across steps | 1.8 | cc:done [7300845] |

---

## Phase 2: Real LLM proposer (the untrusted component)

| Task | Content | DoD | Depends | Status |
|------|---------|-----|---------|--------|
| 2.1  | Wire Claude API client for LLM proposals | Claude API initialized, can call `messages.create()` with tool schema | Phase 1 | cc:done [f5b154a] |
| 2.2  | Implement LLM-based proposer reading AgentDojo observations | LLM sees transaction history (including injected payload), proposes tool calls | 2.1 | cc:todo |
| 2.3  | End-to-end test: real LLM vs. injection_incoming_transaction | LLM proposes legitimate calls + injection, base blocks injection, audit trail complete | 2.2 | cc:todo |
| 2.4  | Verify guarantee holds: injection blocked with real LLM | `uv run pytest` passes; injection blocked; LLM proposals logged | 2.3 | cc:todo |
| 2.5  | Test with full AgentDojo banking suite (all scenarios) | All banking scenarios run without crashes; injection_* scenarios all blocked | 2.4 | cc:todo |
| 2.6  | Measure attack success rate on AgentDojo banking | P3 claim ready: report 0% injection success on banking suite (or lower bound) | 2.5 | cc:todo |

## Backlog

- Phase 3: Measure and report honestly (comprehensive benchmark across all AgentDojo suites)
- Hardening (Sketch 4 proper — cryptographic signing, distributed trust)
- Engineering / hygiene (performance, error handling, docs)
