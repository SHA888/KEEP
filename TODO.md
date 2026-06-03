# KEEP — TODO

Atomic, comprehensive task list for the KEEP probe. Status: `[x]` done · `[~]` in progress · `[ ]` open.
Each item is a single, independently-completable unit. Keep every guarantee stated as a four-field
claim (see `CLAUDE.md`); never claim a measured result that has not been measured.

## P0 — Core mechanism (done)

- [x] `Capability` value: tool + scope (exact-match arg constraints) + nonce
- [x] `TrustedBase`: mint / authorize / execute + audit log (the TCB; no LLM in its trust path)
- [x] `deriver.derive`: trusted structured task → capability set (the labeling seam)
- [x] `UntrustedAgent` stub: proposes `(tool, args)`, can be fully attacker-controlled
- [x] `runner.run`: task → mint → propose → authorize → execute
- [x] Impossibility test: injection blocked with a fully compromised agent
- [x] Seam test: in-scope misuse is NOT blocked (the limit encoded as a passing test)
- [x] README four-field claim, `THREAT.md`, `LICENSE`, `CLAUDE.md`, git remote + push

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

## P2 — Real LLM proposer (the untrusted component)

- [ ] Add an LLM client (Anthropic SDK; configurable model) as `UntrustedAgent`
- [ ] API key via env var only; no secrets in the repo or in logs
- [ ] Plumb model tool-calls → parsed `(tool, args)` proposals (structured output)
- [ ] Verify the LLM has NO execution path — it only proposes; the base authorizes
- [ ] Confirm: when the injection persuades the model to emit the attacker call, the base blocks it
- [ ] Smoke test: full scenario with a real model — injection blocked, legit action proceeds

## P3 — Measure and report honestly

- [ ] Harness to run N scenarios / injection variants and compute attack success rate (ASR)
- [ ] Run the chosen AgentDojo subset; record ASR (target: **0%** on the scoped guarantee)
- [ ] Record AgentDojo's undefended baseline ASR for the same subset (cite numbers)
- [ ] Measure utility / task-success too — blocking is not completing (the honest cost)
- [ ] Widen the deriver (structured task → free-form NL) and measure where the guarantee degrades
- [ ] `RESULTS.md`: the four-field claim revisited against measured data; report any successes and why
- [ ] Update README/CLAUDE.md status; only now may "benchmarked" replace "structural + simulated"

## Hardening (Sketch 4 proper — as needed, not blocking the probe)

- [ ] Cryptographic capabilities: signed unforgeable tokens, not just a single-process registry
- [ ] Enforce capability expiry and nonce/replay protection (nonce is currently unchecked)
- [ ] Test the coercion path (UNTRUST §7): confirm no path lets untrusted data cause a `mint`
- [ ] Structured, persisted, machine-readable audit log

## Engineering / hygiene

- [ ] GitHub Actions CI: run `pytest` on push
- [ ] Lint + type-check (ruff, mypy)
- [ ] Lockfile for reproducible installs

## Decisions (owner: human)

- [ ] License decision before any reuse grant (currently all-rights-reserved placeholder)
- [ ] Whether to fold a measured P3 result back into UNTRUST §15.6 (coordinate via the cross-link)
