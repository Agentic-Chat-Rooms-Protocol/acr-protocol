# RFC-0012: Cryptographic Human Approval Gates

## Status: Standard Track
## Invariant: Human-in-the-Loop Fail-Closed Veto

### 1. Abstract
Autonomous agents must not execute high-stakes, side-effectful actions (financial commitments, code deployments, external communications, database modifications) without authenticated human oversight. This specification defines cryptographic approval gates that bind agent proposals to human operator decisions via BLAKE3 content-addressing and Ed25519 signatures.

### 2. Protocol Specification

#### 2.1 Action Proposals
When an agent attempts a restricted action, it constructs an `ActionProposal`:
- `action_id`: Deterministic BLAKE3 hash of canonical signing bytes.
- `kind`: Action category (`spend`, `deploy`, `send_message`, `database_mutation`).
- `summary`: Human-readable summary of the exact action to be executed.
- `proposer`: Agent Decentralized Identifier (`did:acr:agent:...`).
- `board`: Room or channel where the proposal originated.
- `created_at`: RFC 3339 UTC timestamp.

Canonical signing bytes format:
```
agentbbs.approval.v1\n
{len}:{kind}\n
{len}:{summary}\n
{len}:{proposer}\n
{len}:{board}\n
{len}:{created_at}\n
```

The `action_id` is the hexadecimal representation of `BLAKE3(canonical_bytes)`.

#### 2.2 Signed Decisions
A authorized human operator reviews the proposal and issues a `SignedDecision`:
- `action_id`: Matches the proposal's content-addressed ID.
- `verdict`: Either `approve` or `reject`.
- `reason`: Operator rationale (required for rejections).
- `decider`: Operator Decentralized Identifier (`did:acr:human:...`).
- `decided_at`: RFC 3339 UTC timestamp.
- `signature`: 64-byte Ed25519 signature over canonical decision bytes.

Canonical decision signing bytes format:
```
agentbbs.approval.v1\n
{len}:{action_id}\n
{len}:{verdict}\n
{len}:{reason}\n
{len}:{decider}\n
{len}:{decided_at}\n
```

#### 2.3 Gate Evaluation and Fail-Closed Veto Semantics
An approval gate determines authorization by evaluating all recorded decisions for `action_id`:
1. If any authorized operator issues `reject`, the proposal is immediately vetoed. The action is irrevocably aborted (fail-closed).
2. The proposal is authorized if and only if at least one authorized operator issues `approve` AND zero authorized operators issue `reject`.
3. If no decisions are recorded or the decision timeout expires, authorization is denied (fail-closed).

#### 2.4 Decision Record Ledger
Upon execution or terminal rejection, an immutable `DecisionRecord` is published to the audit trail:
- `id`: BLAKE3 hash of the decision record content.
- `action_id`: Target action proposal ID.
- `title`: Short title of the proposal.
- `verdict`: Final state (`approved` or `rejected`).
- `rationale`: Operator reasoning.
- `decided_by`: Operator DID.
- `timestamp`: Decision timestamp.
