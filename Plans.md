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
| 1.5  | Adapter: AgentDojo tool schema → KEEP capability scope | Adapter generates capabilities for all AgentDojo tools | 1.4 | cc:todo |
| 1.6  | Route every AgentDojo tool call through `TrustedBase.authorize` | All calls intercepted; audit log recorded | 1.5 | cc:todo |
| 1.7  | Reproduce one documented banking injection end-to-end | Injection scenario runs against real environment | 1.6 | cc:todo |
| 1.8  | Test: real-scenario injection blocked by base | `uv run pytest` passes; injection blocked; logs show decision | 1.7 | cc:todo |
| 1.9  | Handle multi-step tasks: capability lifecycle across episode | Capabilities expire/renew correctly across steps | 1.8 | cc:todo |

## Backlog

- Phase 2: Real LLM proposer (the untrusted component)
- Phase 3: Measure and report honestly
- Hardening (Sketch 4 proper)
- Engineering / hygiene
