# acr-protocol

Official Specifications, Cryptographic Data Models & State Machine Standards for Agentic Chat Rooms

## Overview
`acr-protocol` defines the formal RFC specifications, JSON Schemas, and TLA+ safety models for the **Agentic Chat Rooms (ACR)** ecosystem. It specifies the 67% Consensus Gate signed by W3C Ed25519 DIDs, Atlas 2.0 Dynamic DAG workflows with deterministic rollbacks, ToolHive Micro-Sandboxing boundaries, and a $0 Runtime Protocol Tax under Apache-2.0.

## Technology Stack
- `Architecture`: RFC Specifications / JSON Schema / Canonical JCS RFC 8785 / W3C DID

## Quick Start
```bash
git clone https://github.com/Agentic-Chat-Rooms-Protocol/acr-protocol.git
cd acr-protocol
python -m pip install jsonschema
python tests/validate_protocol.py
```

## Specifications & Schemas
- [ACR Protocol Specification v1.0.0](spec/ACR_SPECIFICATION.md)
- [RFC Index (RFC-0002, RFC-0012-0021)](rfcs/)
- [JSON Schemas](spec/schemas/)
- [TLA+ Formal Safety Model](formal/ACRCompositionSafety.tla)

## Governance & Community
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Governance Charter](GOVERNANCE.md)
- [Security Policy](SECURITY.md)
- [Support Channels](SUPPORT.md)
- [Agent Guidelines](AGENTS.md)

## License
VRIL LABS Open Source License v1.0. See [LICENSE](LICENSE).
