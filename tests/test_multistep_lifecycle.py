"""Multi-step capability lifecycle tests (Task 1.9).

This module tests capability renewal and expiration across multi-step scenarios.
It demonstrates that the KEEP guarantee holds even when:
1. An agent makes multiple calls across steps
2. Capabilities are consumed (renewal decrements)
3. Once a capability is exhausted, no further use is possible
4. The guarantee is enforced structurally, not by the model

Scenario: A multi-step banking task where the agent must reconcile an account.
- Step 1: list_transactions (authorized for 1 use)
- Step 2: get_balance (authorized for 1 use)
- Step 3: Agent tries to call list_transactions again (blocked, renewal exhausted)
"""

import pytest


def test_capability_consumed_after_use():
    """Verify that a capability with renewal=1 is consumed after one use.

    This tests the structural guarantee for multi-step scenarios: capabilities
    are consumed (renewal decrements) on use, and cannot be reused once exhausted.
    """
    from keep.base import TrustedBase
    from keep.capability import Capability

    base = TrustedBase()

    # Mint one capability for get_balance with renewal=1 (one-shot)
    base.mint(
        Capability(
            tool="get_balance",
            scope=(),
            nonce="cap-balance-check",
            renewal=1,
        )
    )

    executed_calls = []

    def effect(tool: str, args: dict) -> dict:
        executed_calls.append((tool, args))
        return {"status": "success", "balance": 5000.0}

    # Step 1: Agent calls get_balance (should succeed)
    result1 = base.execute("get_balance", {}, effect)
    assert result1 == {"status": "success", "balance": 5000.0}
    assert len(executed_calls) == 1

    # Step 2: Agent calls get_balance again (should fail, renewal exhausted)
    with pytest.raises(Exception) as exc_info:
        base.execute("get_balance", {}, effect)
    assert "No capability authorizes" in str(exc_info.value)
    assert len(executed_calls) == 1  # No additional call executed


def test_multistep_scenario_with_mixed_renewal():
    """Multi-step scenario with different renewal counts for different capabilities.

    User task: "Check my balance and recent transactions (up to 5)"
    - get_balance: authorized, renewal=1 (can use once)
    - list_transactions with limit=5: authorized, renewal=2 (can use twice)

    Agent steps:
    1. list_transactions(limit=5) — authorized, renewal becomes 1 ✓
    2. get_balance() — authorized, renewal becomes 0 ✓
    3. list_transactions(limit=5) — authorized, renewal becomes 0 ✓
    4. list_transactions(limit=5) — NOT authorized, renewal is 0 ✗
    5. get_balance() — NOT authorized, renewal is 0 ✗
    """
    from keep.base import TrustedBase
    from keep.capability import Capability

    base = TrustedBase()

    # Mint capabilities from user task
    base.mint(
        Capability(
            tool="get_balance",
            scope=(),
            nonce="cap-balance",
            renewal=1,
        )
    )
    base.mint(
        Capability(
            tool="list_transactions",
            scope=(("limit", 5),),
            nonce="cap-list-tx",
            renewal=2,
        )
    )

    executed_calls = []

    def effect(tool: str, args: dict) -> object:
        executed_calls.append((tool, args))
        if tool == "get_balance":
            return {"status": "success", "balance": 5000.0}
        elif tool == "list_transactions":
            return {
                "status": "success",
                "transactions": [
                    {"id": 1, "amount": 100},
                    {"id": 2, "amount": 200},
                ],
            }
        else:
            raise ValueError(f"Unknown tool: {tool}")

    # Agent proposes multi-step calls
    agent_proposals = [
        ("list_transactions", {"limit": 5}),  # Step 1: authorized, renewal 2->1
        ("get_balance", {}),  # Step 2: authorized, renewal 1->0
        ("list_transactions", {"limit": 5}),  # Step 3: authorized, renewal 1->0
        (
            "list_transactions",
            {"limit": 5},
        ),  # Step 4: NOT authorized, renewal exhausted
        ("get_balance", {}),  # Step 5: NOT authorized, renewal exhausted
    ]

    results = []
    for tool, args in agent_proposals:
        try:
            result = base.execute(tool, args, effect)
            results.append(("ok", result))
        except Exception as exc:
            results.append(("blocked", str(exc)))

    # Verify results
    assert results[0][0] == "ok"  # Call 1: authorized
    assert results[1][0] == "ok"  # Call 2: authorized
    assert results[2][0] == "ok"  # Call 3: authorized
    assert (
        results[3][0] == "blocked"
    )  # Call 4: NOT authorized (list_transactions renewal exhausted)
    assert (
        results[4][0] == "blocked"
    )  # Call 5: NOT authorized (get_balance renewal exhausted)

    # Verify only the first 3 calls executed
    assert len(executed_calls) == 3
    assert executed_calls[0] == ("list_transactions", {"limit": 5})
    assert executed_calls[1] == ("get_balance", {})
    assert executed_calls[2] == ("list_transactions", {"limit": 5})

    # Verify audit trail shows consumption
    audit = base.audit
    # Find the authorize entries and check renewal tracking
    authorize_entries = [
        e for e in audit if e[0] == "authorize" and e[3]
    ]  # successful authorizations
    assert len(authorize_entries) == 3  # 3 successful authorizations
    # Check the renewal counts decreased
    assert (
        authorize_entries[0][4] == "cap-list-tx" and authorize_entries[0][5] == 1
    )  # renewal became 1
    assert (
        authorize_entries[1][4] == "cap-balance" and authorize_entries[1][5] == 0
    )  # renewal became 0
    assert (
        authorize_entries[2][4] == "cap-list-tx" and authorize_entries[2][5] == 0
    )  # renewal became 0


def test_injection_blocked_in_multistep_with_exhausted_capability():
    """Multi-step scenario where injection targets a capability that's already exhausted.

    User task: "Check balance once"
    - get_balance: authorized, renewal=1

    Attacker's goal: Call get_balance multiple times to drain account monitoring

    Expected: Injection blocked because capability is exhausted after first use.
    """
    from keep.base import TrustedBase
    from keep.capability import Capability

    base = TrustedBase()

    # User only authorized one balance check
    base.mint(
        Capability(
            tool="get_balance",
            scope=(),
            nonce="cap-balance-once",
            renewal=1,
        )
    )

    executed_calls = []

    def effect(tool: str, args: dict) -> dict:
        executed_calls.append((tool, args))
        return {"status": "success", "balance": 5000.0}

    # Compromised agent that tries to call get_balance twice
    agent_proposals = [
        ("get_balance", {}),  # Legitimate: user authorized this
        ("get_balance", {}),  # Injection: agent tries to repeat
    ]

    results = []
    for tool, args in agent_proposals:
        try:
            result = base.execute(tool, args, effect)
            results.append(("ok", result))
        except Exception as exc:
            results.append(("blocked", str(exc)))

    # Verify the injection is blocked
    assert results[0][0] == "ok"  # First call authorized
    assert results[1][0] == "blocked"  # Second call blocked

    # Verify only one call executed
    assert len(executed_calls) == 1
    assert executed_calls[0] == ("get_balance", {})

    # Verify audit trail
    blocked_entries = [e for e in base.audit if e[0] == "BLOCKED"]
    assert len(blocked_entries) == 1
    assert blocked_entries[0] == ("BLOCKED", "get_balance", {})


def test_capability_with_unlimited_renewal():
    """Capability with renewal > 1 can be reused across multiple steps.

    This demonstrates that the lifecycle model is flexible: some capabilities
    (renewal=1) are one-shot, while others (renewal>1) can be reused.

    User task: "Reconcile account: check balance up to 3 times"
    - get_balance: authorized, renewal=3
    """
    from keep.base import TrustedBase
    from keep.capability import Capability

    base = TrustedBase()

    # Capability with renewal=3 (can be used 3 times)
    base.mint(
        Capability(
            tool="get_balance",
            scope=(),
            nonce="cap-balance-triple",
            renewal=3,
        )
    )

    executed_calls = []

    def effect(tool: str, args: dict) -> dict:
        executed_calls.append((tool, args))
        return {"status": "success", "balance": 5000.0}

    # Agent makes 4 calls
    for i in range(4):
        try:
            base.execute("get_balance", {}, effect)
        except Exception:
            pass  # Expected to fail on 4th call

    # First 3 calls should succeed
    assert len(executed_calls) == 3

    # 4th call should be blocked
    with pytest.raises(Exception) as exc_info:
        base.execute("get_balance", {}, effect)
    assert "No capability authorizes" in str(exc_info.value)
    assert len(executed_calls) == 3  # Still 3, 4th was blocked
