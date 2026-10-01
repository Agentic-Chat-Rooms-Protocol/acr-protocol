# RFC-0016: Declarative Step Playbook Workflows

## Status: Standard Track
## Invariant: Content-Addressed Workflow Integrity & Automatic Gate Parking

### 1. Abstract
Deliberation and autonomous multi-agent task execution must follow deterministic, auditable workflows that pause safely when crossing human authority boundaries. This specification defines declarative Playbooks (`agentbbs.playbook.v1`) and their execution state machines featuring automatic gate parking.

### 2. Protocol Specification

#### 2.1 Playbook Data Model
A Playbook is a content-addressed sequence of steps:
- `playbook_id`: Hex-encoded 32-byte BLAKE3 hash of canonical playbook definition bytes.
- `name`: Human-readable workflow title.
- `version`: Version identifier string.
- `trigger`: Kickoff condition (`manual`, `event`, `cron`).
- `steps`: Ordered list of `PlaybookStep` definitions.

Canonical signing bytes format:
```
agentbbs.playbook.v1\n
{len}:{name}\n
{len}:{version}\n
{len}:{trigger}\n
{len}:{step_count}\n
```
Followed by serialized representations of each step.

#### 2.2 Step Kinds
Each step contains an identifier and one of three typed specifications:
1. `AgentTask`: Specifies `{ agent: string, instruction: string }`. Dispatches work to an autonomous agent.
2. `ApprovalGate`: Specifies `{ summary: string }`. Establishes a mandatory human authorization gate.
3. `Tool`: Specifies `{ tool: string }`. Invokes a verified local or MCP tool.

#### 2.3 Runner State Machine
The runner advances step-by-step through the playbook:
- `status`: Lifecycle indicator (`running`, `awaiting_approval`, `completed`, `failed`).
- `cursor`: Zero-based index of the active step.
- `steps_completed`: Count of finalized steps.

State transitions:
1. When entering an `AgentTask` or `Tool` step, status remains `running`. Upon successful execution, `cursor` advances.
2. When entering an `ApprovalGate` step:
   - The runner transitions immediately to `awaiting_approval`.
   - Execution is parked; no further steps execute.
   - An `ActionProposal` is generated for operator review.
3. Resumption:
   - If an authorized operator submits a valid `SignedDecision` with verdict `approve`, the runner transitions back to `running` and advances `cursor`.
   - If any authorized operator submits `reject` (veto), the runner transitions to `failed` and terminates.
4. When `cursor == len(steps)`, status transitions to `completed`.
