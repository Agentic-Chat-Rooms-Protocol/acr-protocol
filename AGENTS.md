# Agent Guidelines - acr-protocol

## Specification & Modeling Discipline
1. **Deterministic Serialization**: All cryptographic message hashes and Merkle DAG states MUST use deterministic RFC 8785 JSON Canonicalization Scheme (JCS).
2. **Identity Invariant**: Identities MUST resolve to W3C Decentralized Identifiers (`did:key` or `did:web`). Raw non-cryptographic strings are rejected.
3. **Consensus Voting Invariant (GAP-08)**: Every `DISSENT` vote on proposal ballots MUST provide a non-empty cryptographic rationale string.
4. **Zero-Trust Capability Scoping**: All inter-agent tool actions require explicit Verifiable Credential capability grants.
