# Plans

## P1 — Wire the real AgentDojo benchmark

- [ ] Add `pyproject.toml` (src layout) so the package installs with `pip install -e .`
- [ ] Pin AgentDojo as a dependency; record the exact version
- [ ] Identify and document the specific banking-suite scenario(s) by ID in `THREAT.md`
- [ ] Adapter: AgentDojo user task → KEEP deriver input (the trusted instruction)
- [ ] Adapter: AgentDojo tool schema → KEEP capability scope (decide which args are scoped)
- [ ] Route every AgentDojo tool call through `TrustedBase.authorize` before execution
- [ ] Reproduce one documented banking injection end-to-end against the real environment
- [ ] Test: the real-scenario injection is blocked by the base (scripted agent, real env)
- [ ] Handle multi-step tasks: capability lifecycle across a full AgentDojo episode

## Backlog

- P2 — Real LLM proposer (the untrusted component)
- P3 — Measure and report honestly
- Hardening (Sketch 4 proper)
- Engineering / hygiene
