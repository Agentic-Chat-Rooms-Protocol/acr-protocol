#!/usr/bin/env python3
"""Validation suite for acr-protocol specifications, RFCs, and JSON schemas."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "spec" / "schemas"
SPEC_FILE = ROOT / "spec" / "ACR_SPECIFICATION.md"
RFCS_DIR = ROOT / "rfcs"

EXPECTED_SCHEMAS = {
    "agent_card.json",
    "approval_gate.json",
    "audit_block.json",
    "capabilities_governance.json",
    "identity_attestation.json",
    "playbook_workflow.json",
    "postguard_pii.json",
    "process_milestone_thread.json",
    "proposal_ballot.json",
    "reputation_score.json",
    "rotation_link.json",
    "vector_memory_rvf.json",
    "webtrust_endorsement.json",
}

CANONICAL_18_WORKFLOWS = [
    "postgres-split-brain",
    "egress-token-anomaly",
    "ingress-oom-autoscaling",
    "canary-deployment-rollback",
    "code-review-tla-verification",
    "saif-compliance-audit",
    "bft-consensus-deliberation",
    "twinseal-passkey-approval",
    "durable-wal-recovery",
    "context-compaction-pruning",
    "byzantine-fault-slashing",
    "identity-key-rotation",
    "micro-sandbox-isolation",
    "cross-model-agentflex-synthesis",
    "declarative-step-playbook",
    "postguard-injection-defense",
    "dynamic-dag-topology",
    "transitive-trust-federation",
]

CANONICAL_11_REMOTE_TOOLS = [
    "acr_create_room",
    "acr_list_workflows",
    "acr_get_workflow",
    "acr_configure_workflow",
    "acr_get_workflow_status",
    "acr_list_rooms",
    "acr_room_status",
    "acr_room_ledger_tail",
    "acr_room_send",
    "acr_room_consensus",
    "acr_container_status",
]


def load_schemas() -> dict[str, dict]:
    found = {p.name for p in SCHEMAS_DIR.glob("*.json")}
    missing = EXPECTED_SCHEMAS - found
    assert not missing, f"Missing expected schemas: {sorted(missing)}"

    schemas: dict[str, dict] = {}
    for path in sorted(SCHEMAS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "$schema" in data, f"{path.name} missing $schema"
        assert "title" in data, f"{path.name} missing title"
        assert data.get("type") == "object", f"{path.name} root type must be object"
        validator_cls = jsonschema.validators.validator_for(data)
        validator_cls.check_schema(data)
        schemas[path.name] = data
    return schemas


def validate_definition(schema: dict, def_name: str, instance: dict) -> None:
    subschema = {
        "$schema": schema["$schema"],
        "$ref": f"#/definitions/{def_name}",
        "definitions": schema["definitions"],
    }
    Draft202012Validator(subschema).validate(instance)


def test_schema_fixtures(schemas: dict[str, dict]) -> None:
    hex64 = "a" * 64
    hex128 = "b" * 128
    hex16 = "c" * 16

    # 1. agent_card.json (positive + negative)
    Draft202012Validator(schemas["agent_card.json"]).validate(
        {
            "did": "did:key:z6MkhaXgBZDvotDkL5257faiz4898XnpLFimqCpvzIV8eE9g",
            "name": "sentinel-01",
            "role": "sentinel",
            "status": "online",
            "capabilities": ["vote", "audit"],
        }
    )
    try:
        Draft202012Validator(schemas["agent_card.json"]).validate(
            {
                "did": "not-a-did",
                "name": "bad",
                "role": "agent",
                "status": "online",
                "capabilities": [],
            }
        )
        raise AssertionError("Invalid DID should fail agent_card.json")
    except ValidationError:
        pass

    # 2. audit_block.json
    Draft202012Validator(schemas["audit_block.json"]).validate(
        {
            "index": 0,
            "timestamp": "2026-11-18T00:00:00Z",
            "event_type": "VOTE_DISSENT_RECORDED",
            "state_hash": hex64,
            "prev_hash": "0" * 64,
            "payload": {"proposal_id": "prop-1"},
        }
    )

    # 3. proposal_ballot.json (positive + empty dissent rationale rejected)
    Draft202012Validator(schemas["proposal_ballot.json"]).validate(
        {
            "id": "prop-1",
            "room_id": "room-1",
            "title": "Enable loopback guard",
            "status": "passed",
            "proposer_did": "did:key:z6MkhaXgBZDvotDkL5257faiz4898XnpLFimqCpvzIV8eE9g",
            "votes": {"did:key:z6Mk1": "APPROVE"},
            "dissent_logs": [
                {
                    "voter_did": "did:key:z6Mk2",
                    "rationale": "Needs extra rollout window",
                    "timestamp": "2026-11-18T00:00:00Z",
                }
            ],
        }
    )
    try:
        Draft202012Validator(schemas["proposal_ballot.json"]).validate(
            {
                "id": "prop-1",
                "room_id": "room-1",
                "title": "Enable loopback guard",
                "status": "open",
                "proposer_did": "did:key:z6Mk1",
                "votes": {},
                "dissent_logs": [
                    {"voter_did": "did:key:z6Mk2", "rationale": "", "timestamp": "2026-11-18T00:00:00Z"}
                ],
            }
        )
        raise AssertionError("Empty dissent rationale must fail proposal_ballot.json")
    except ValidationError:
        pass

    # 4. approval_gate.json
    validate_definition(
        schemas["approval_gate.json"],
        "ActionProposal",
        {
            "action_id": hex64,
            "kind": "deploy",
            "summary": "Roll out release v1.0.0",
            "proposer": "did:acr:agent:ops-01",
            "board": "ops-room",
            "created_at": "2026-11-18T00:00:00Z",
        },
    )
    validate_definition(
        schemas["approval_gate.json"],
        "SignedDecision",
        {
            "action_id": hex64,
            "verdict": "approve",
            "reason": "Verified checks",
            "decider": "did:acr:human:alice",
            "decided_at": "2026-11-18T00:01:00Z",
            "signature": hex128,
        },
    )

    # 5. capabilities_governance.json
    validate_definition(
        schemas["capabilities_governance.json"],
        "VerifiedRoleResult",
        {"granted_role": "moderator", "caps_bitmask": 31, "valid": True},
    )
    try:
        validate_definition(schemas["capabilities_governance.json"], "CapsBitmask", 1024)
        raise AssertionError("Bitmask > 1023 must fail")
    except ValidationError:
        pass

    # 6. playbook_workflow.json
    validate_definition(
        schemas["playbook_workflow.json"],
        "Playbook",
        {
            "playbook_id": hex64,
            "name": "postgres-split-brain",
            "version": "1.0.0",
            "trigger": "event",
            "steps": [{"id": "step_1", "kind": "approval_gate", "summary": "Confirm failover"}],
        },
    )
    validate_definition(
        schemas["playbook_workflow.json"],
        "PlaybookRun",
        {
            "playbook_id": hex64,
            "cursor": 0,
            "status": "awaiting_approval",
            "steps_completed": 0,
        },
    )

    # 7. rotation_link.json, reputation_score.json, identity_attestation.json, postguard_pii.json,
    #    process_milestone_thread.json, vector_memory_rvf.json, webtrust_endorsement.json
    validate_definition(
        schemas["rotation_link.json"],
        "RotationLink",
        {
            "predecessor": hex64,
            "successor": hex64,
            "timestamp": "2026-11-18T00:00:00Z",
            "predecessor_sig": hex128,
            "successor_sig": hex128,
        },
    )
    validate_definition(
        schemas["reputation_score.json"],
        "ReputationScore",
        {"agent": hex64, "successes": 9.0, "total": 10.0, "rate": 0.9, "score": 0.59},
    )
    validate_definition(
        schemas["identity_attestation.json"],
        "ChallengeNonce",
        {
            "nonce": hex64,
            "created_at": "2026-11-18T00:00:00Z",
            "expires_at": "2026-11-18T00:01:00Z",
        },
    )
    validate_definition(
        schemas["postguard_pii.json"],
        "EgressSanitization",
        {"redacted_keys_count": 1, "sanitized_payload": {"token": "[REDACTED]"}},
    )
    validate_definition(
        schemas["process_milestone_thread.json"],
        "MilestoneThread",
        {
            "milestone": {
                "milestone_id": "ms-1",
                "title": "Run DAG validation",
                "status": "completed",
                "agent": "did:acr:agent:verifier",
                "step_count": 1,
                "started_at": "2026-11-18T00:00:00Z",
            },
            "steps": [
                {
                    "step_id": "st-1",
                    "milestone_id": "ms-1",
                    "step_type": "tool_call",
                    "content": "validate",
                    "duration_ms": 12,
                    "status": "success",
                }
            ],
        },
    )
    validate_definition(
        schemas["vector_memory_rvf.json"],
        "LshIndex",
        {"dim": 64, "bits": 64, "sigs": [hex16], "planes_count": 64},
    )
    validate_definition(
        schemas["webtrust_endorsement.json"],
        "TrustDistanceQuery",
        {"roots": [hex64], "target": hex64, "max_depth": 3},
    )


def test_specification_and_rfcs() -> None:
    spec_text = SPEC_FILE.read_text(encoding="utf-8")
    assert "Version 1.0.0 (November 2026)" in spec_text, "Spec must declare Version 1.0.0 (November 2026)"
    assert "v0.8.2" not in spec_text, "Spec must not retain stale v0.8.2 version"

    for rfc_num in ["RFC-0002"] + [f"RFC-{n:04d}" for n in range(12, 22)]:
        assert rfc_num in spec_text, f"Spec missing reference to {rfc_num}"
        matches = list(RFCS_DIR.glob(f"{rfc_num}-*.md"))
        assert matches, f"Missing RFC file for {rfc_num}"
        assert matches[0].read_text(encoding="utf-8").strip(), f"Empty RFC file: {matches[0].name}"

    for wf in CANONICAL_18_WORKFLOWS:
        assert wf in spec_text, f"Spec missing canonical workflow {wf}"

    for tool in CANONICAL_11_REMOTE_TOOLS:
        assert tool in spec_text, f"Spec missing canonical Remote MCP tool {tool}"

    for required_term in [
        "https://mcp.agentchatrooms.dev/mcp",
        "https://clerk.agentchatrooms.dev",
        '"profile", "email"',
        "workflow-catalog.json",
        "execution_supported: false",
        "room_limit_reached",
        "workflow_conflict",
        "BranchPath",
        "OUTCOME_UNKNOWN",
        "DurableCommandWal",
        "127.0.0.1:20443",
        "20444",
        "20445",
        "20447",
        "acr-opsroom",
        "`false` Default",
        "HostGuard",
        "OriginGuard",
        "ACR_API_TOKEN",
        "ValidateLocal",
        "noRedirect",
        "security@agentchatrooms.dev",
        "support@agentchatrooms.dev",
        "conduct@agentchatrooms.dev",
        "privacy@agentchatrooms.dev",
    ]:
        assert required_term in spec_text, f"Spec missing required architecture primitive: {required_term}"

    # Ensure client OAuth scope request prohibition is honored and legacy domain is absent
    assert "MUST NOT** request custom resource scopes" in spec_text
    for md_path in ROOT.rglob("*.md"):
        txt = md_path.read_text(encoding="utf-8")
        assert "vrillabs.com" not in txt.lower(), f"Forbidden vrillabs.com in {md_path.relative_to(ROOT)}"
        assert "acr.network" not in txt.lower(), f"Forbidden acr.network in {md_path.relative_to(ROOT)}"


def test_markdown_links() -> None:
    link_re = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]*)?\)")
    for md_path in [ROOT / "README.md", SPEC_FILE]:
        text = md_path.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (md_path.parent / target).resolve()
            assert resolved.exists(), f"Broken relative link in {md_path.relative_to(ROOT)}: {target}"


def main() -> int:
    schemas = load_schemas()
    test_schema_fixtures(schemas)
    test_specification_and_rfcs()
    test_markdown_links()
    print(f"OK: validated {len(schemas)} JSON schemas, 11 RFCs, 18 workflows, 11 Remote MCP tools, and spec links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
