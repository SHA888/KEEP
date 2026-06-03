# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in the **KEEP** repository.

## What this repo is

KEEP is an **implementation probe**, spun out from the UNTRUST thinking project
([github.com/SHA888/UNTRUST](https://github.com/SHA888/UNTRUST)). It tests one claim:
that a documented prompt-injection attack can be made **provably impossible** for a narrow
task — not statistically mitigated — by moving all action authority out of the language model
and into a small trusted base (UNTRUST Sketch 4 — capability tokens — under the §10 trusted-base
synthesis).

This is a **codebase**, unlike UNTRUST (which is a single-document thinking project). There is
code to run and tests to pass here. But it is a *probe*, not a product or framework.

## Relationship to UNTRUST (read this first)

- KEEP is a **separate repo with its own scope, license, and name**, per UNTRUST's distribution
  rules. **Do not** commit KEEP material into the UNTRUST repo, do not pull UNTRUST material into
  here, and do not use "UNTRUST" as a label/brand for this work. The two repos cross-reference by
  URL only.
- UNTRUST is the *thinking* (what a fix would look like and its honest limits); KEEP is *one build*
  of one sketch. When KEEP and UNTRUST disagree on the conceptual frame, UNTRUST is the source of
  record — but KEEP is free to discover that the sketch does not survive contact with reality, and
  must report that honestly if so.

## The load-bearing discipline (do not drift)

KEEP inherits UNTRUST's anti-overclaim posture. The whole point is to keep a *fix* distinct from a
*mitigation*; blurring that here would defeat the probe.

- **State every guarantee as a four-field claim** (UNTRUST's companion *enforceability discipline*):
  Property / Class / Seam(s) / Out-of-scope. KEEP's top-level claim is in `README.md`; new
  guarantees get the same treatment. A bare "this is secure" is non-conformant.
- **Class A here is conditional, and the conditions are the seams.** KEEP's guarantee is
  `(A, given a correct deriver and a correct base, —)`. The seams — the **deriver** (trusted
  instruction → capability scope), **base correctness**, the **trusted-channel assumption** — are
  named in `README.md` and `THREAT.md`. Never present the enforced core as if it covered a seam.
- **Keep the trusted base small and LLM-free.** The trusted computing base is `src/keep/base.py`
  (+ `capability.py`). No LLM, and no value derived from untrusted data, may enter its trust path.
  Capabilities are minted **only** from the trusted user-instruction channel (`deriver.py`). The
  coercion path (UNTRUST §7) lives at the `TrustedBase.mint` call site — guard it.
- **State seams as tests, not footnotes.** The in-scope-misuse limit is encoded as a *passing*
  test (`tests/test_impossibility.py::test_seam_in_scope_action_is_NOT_blocked`) so it cannot be
  forgotten. New seams get the same: a test that makes the limit executable.
- **Do not claim a measured result you have not measured.** "0% attack success on AgentDojo" is a
  P3 claim and is currently **unmeasured**. Until P3 runs, say "structural argument + simulated
  scenario," not "benchmarked."

## Architecture

```
Untrusted neural component (LLM / stub)   proposes (tool, args) — holds NO authority
        │
        ▼
Trusted base  (src/keep/base.py + capability.py — small, auditable, no LLM)
        - mint(cap): from the trusted instruction only (deriver.py)
        - authorize(tool, args): matches a minted capability, or rejects
        - execute(...): runs the effect only if authorized; logs every decision
        ▼
External effects                          reached only through the base
```

Files:
- `src/keep/capability.py` — the `Capability` value (tool + scope + nonce).
- `src/keep/base.py` — `TrustedBase`: mint / authorize / execute + audit log. **The TCB.**
- `src/keep/deriver.py` — trusted instruction → capabilities. **The labeling seam.**
- `src/keep/agent.py` — the untrusted proposer (a stub in P0; a real LLM in P2).
- `src/keep/runner.py` — wires task → mint → propose → authorize → execute.
- `tests/test_impossibility.py` — the probe: injection blocked even with a compromised agent.
- `THREAT.md` — the scenario, the "provably impossible" claim, and the seams/out-of-scope.

## How to run

```bash
uv sync --dev               # install dev dependencies (pytest)
uv run pytest -q            # run tests
```

## Roadmap / status

- **P0 — done.** Core mechanism + impossibility test on a *simulated* AgentDojo banking injection,
  stub agent. The structural claim is encoded and runnable.
- **P1.** Wire the real AgentDojo banking suite (Debenedetti et al. 2024, arXiv:2406.13352).
- **P2.** Replace the stub agent with a real LLM proposer (the base above it does not change).
- **P3.** Measure attack success rate (target 0% on the chosen scenario) and document the seams
  *empirically*, especially as the deriver widens beyond the narrow structured task.

Update this section and `README.md` when a phase lands.

## Conventions

- **No `Co-Authored-By:` trailers in commit messages.** This applies to all assistant-generated commits, 
  including those produced by Claude Code or any other AI tool. Commit attribution stays with the human 
  author. Boilerplate trailers add noise to the history without conveying meaningful authorship and have 
  been retroactively stripped from past commits.
- **English-only requirement:**
  - All Plans.md content must be in English (headers, table columns, task descriptions, status markers).
  - No Japanese characters in Plans.md status markers (use `cc:done` instead of `cc:完了`, `cc:wip` instead 
    of `cc:WIP`, etc).
  - All harness output and documentation must be in English.
  - This applies strictly to tracked files; commit to this constraint when editing Plans.md.
- **Commit/push only when asked.** If on the default branch (`main`), that is the working branch
  for this probe; small probe commits directly on `main` are fine when the user requests them.
- **License:** all rights reserved (placeholder, `LICENSE`). The repo is public on GitHub but not
  licensed for reuse; a real license decision precedes any reuse grant.
