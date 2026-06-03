"""Wire it together: trusted task -> mint -> (untrusted) propose -> authorize -> execute.

The control flow is the architecture (UNTRUST §10): capabilities come from the trusted
task; proposals come from the untrusted agent; only authorized proposals reach effects.
"""
from __future__ import annotations

from typing import Callable

from . import deriver
from .agent import UntrustedAgent
from .base import TrustedBase, Unauthorized


def run(user_task: dict, agent: UntrustedAgent, effect: Callable[[str, dict], object]):
    """Returns (base, results); results[i] is ('ok', value) or ('blocked', reason)."""
    base = TrustedBase()
    for cap in deriver.derive(user_task):  # mint ONLY from the trusted channel
        base.mint(cap)

    results = []
    for tool, args in agent.propose():
        try:
            results.append(("ok", base.execute(tool, args, effect)))
        except Unauthorized as exc:
            results.append(("blocked", str(exc)))
    return base, results
