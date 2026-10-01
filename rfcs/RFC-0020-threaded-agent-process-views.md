# RFC-0020: Threaded Agent Process Views

## Status: Standard Track
## Invariant: Dual-Granularity Process Representation

### 1. Abstract
Autonomous agent deliberation and multi-step plan execution produce extensive debug and tool traces. Displaying all granular tool steps in the primary chat feed causes information overload for human operators. This specification defines threaded process representation, distinguishing high-level milestones (`MessageKind::Milestone`) from granular execution steps (`MessageKind::Step`) in collapsible hierarchies.

### 2. Protocol Specification

#### 2.1 Process Message Kinds
Process-related messages declare a distinct `kind` attribute:
- `milestone`: A primary goal checkpoint, decision boundary, or phase completion summary. Displayed persistently in the main discussion view.
- `step`: A subordinate execution trace, tool call invocation, or intermediate model deliberation snippet. Grouped under its parent milestone.

#### 2.2 Milestone Data Model
A `ProcessMilestone` encapsulates a high-level achievement:
- `milestone_id`: Content-addressed or UUID identifier.
- `title`: Concise human-readable accomplishment description.
- `status`: Execution state (`pending`, `in_progress`, `completed`, `failed`).
- `agent`: DID of the responsible agent.
- `step_count`: Total number of subordinate steps executed under this milestone.
- `started_at`: RFC 3339 UTC timestamp.
- `completed_at`: Optional RFC 3339 UTC timestamp.

#### 2.3 Step Data Model
A `ProcessStep` records an individual operational trace:
- `step_id`: Unique identifier for the granular trace.
- `milestone_id`: Reference to parent milestone.
- `step_type`: Classification (`tool_call`, `observation`, `thought`, `sub_task`).
- `content`: Trace payload, parameters, or log text.
- `duration_ms`: Execution duration in milliseconds.
- `status`: Execution outcome (`success`, `failure`).

#### 2.4 Rendering Invariant
User interfaces conforming to this specification must render milestones as primary timeline items and provide collapsible accordion or drawer views for granular steps. Collapsed milestone views prevent scroll fatigue while preserving complete verifiable audit traces.
