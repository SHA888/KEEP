# KEEP

**A small trusted base that holds capabilities for an untrusted neural component.**
*Working spin-out from the UNTRUST §10 synthesis — probe stage. v0.0.1.*

## What this is

KEEP is the implementation **probe** for one claim from UNTRUST (a working draft on LLM
trust by enforceability): that a documented prompt-injection attack can be made **provably
impossible** for a narrow task — not statistically mitigated — by moving all action authority
out of the language model and into a small trusted base.

It is not a product, not a framework, not a finished system. It is the "simplest end-to-end
demonstration" UNTRUST §15.6 names: a narrow agent task where a benchmarked injection
(AgentDojo [1]) is **structurally blocked**, with the block argued from the base's construction
rather than measured only as a reduced success rate.

## Relationship to UNTRUST

KEEP is a **spin-out**, per UNTRUST's distribution rules: separate repo, separate scope,
separate license, separate name. UNTRUST is the thinking; KEEP probes one of its sketches
(Sketch 4 — capability tokens) under the §10 trusted-base synthesis. Nothing here is committed
back into the UNTRUST repo, and "UNTRUST" is not used as a label for this work.

> **Parent:** UNTRUST — [github.com/SHA888/UNTRUST](https://github.com/SHA888/UNTRUST). KEEP
> implements the demonstration UNTRUST §15.6 names; the relevant sketch is §7 (capability tokens)
> and the synthesis is §10. The companion *enforceability discipline* in that repo is the lens
> KEEP uses to state its own guarantee honestly (the four-field claim below).

## The thesis, stated as a four-field claim

Applying UNTRUST's companion *enforceability discipline* to KEEP itself — honestly, including
the seams:

- **Property.** No side-effecting action executes unless it matches a capability minted from
  the **trusted user-instruction channel**.
- **Class.** `(A, given a correct deriver and a correct base, —)` — structural: an unauthorized
  action is not a computation the base can perform, *regardless of what the untrusted channel
  (documents, tool outputs) contains*.
- **Seam(s).** the **deriver** (user instruction → capability scope — the labeling /
  autoformalisation seam, UNTRUST §12); **base correctness** (it is software; §14); the
  **trusted-channel assumption** (the user's own instruction is trusted — the model's reading of
  untrusted data is not).
- **Out-of-scope.** *in-scope* misuse (an injection whose target action falls inside the
  user-authorized scope); whether the user's task is wise or correct; **task success** (blocking
  an attack is not completing the task — UNTRUST §14, deceived principals).

The guarantee is deliberately narrow. KEEP makes the **out-of-trusted-scope** action impossible.
It does **not** make the model honest, the task correct, or the user un-deceivable.

## Architecture (§10)

```
Untrusted neural component (LLM)         proposes tool calls — holds NO authority
        │  proposals (tool, args)
        ▼
Trusted base  (small, auditable, no LLM in its trust path)
        - mints capabilities from the user instruction (via the deriver)
        - authorizes each proposed call against the minted capabilities
        - executes only authorized calls; logs every decision
        ▼
External effects (send_money, …)         reached only through the base
```

## Status / roadmap

- **P0 — now.** Core mechanism + an impossibility test on a *simulated* AgentDojo-style banking
  injection. No real LLM or AgentDojo install yet; the test encodes the structural claim.
- **P1.** Wire the real AgentDojo banking suite scenario [1].
- **P2.** A real LLM proposer (the untrusted component).
- **P3.** Measure attack success rate (target: **0%** on the chosen scenario) and document the
  seams *empirically* — especially where the deriver widens.

Run the P0 probe: `python -m pytest -q`  (pure stdlib; no install needed).

## References

[1] **AgentDojo: A Dynamic Environment to Evaluate Attacks and Defenses for LLM Agents.**
Debenedetti, E., Zhang, J., Balunović, M., Beurer-Kellner, L., Fischer, M., & Tramèr, F. (2024).
NeurIPS 2024. arXiv:2406.13352.

## License

All rights reserved (placeholder — see `LICENSE`). A real license decision comes before any
publication or reuse.
