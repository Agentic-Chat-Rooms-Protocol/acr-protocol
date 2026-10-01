# RFC-0017: Transitive Web of Trust Federation

## Status: Standard Track
## Invariant: Cryptographic Endorsements & Rotation-Aware Trust BFS

### 1. Abstract
Decentralized networks of autonomous agents cannot rely on centralized certificate authorities. This specification defines peer-to-peer transitive trust via Ed25519-signed endorsements, depth-bounded breadth-first search (BFS) reachability, and seamless trust inheritance across identity key rotation chains.

### 2. Protocol Specification

#### 2.1 Endorsements
An `Endorsement` is an authenticated statement from one node vouching for another:
- `endorser`: Hex-encoded 32-byte Ed25519 public key of the vouching identity.
- `subject`: Hex-encoded 32-byte Ed25519 public key of the vouched peer.
- `created_at`: RFC 3339 UTC declaration timestamp.
- `signature`: 64-byte Ed25519 signature over canonical endorsement bytes.

Canonical signing bytes format:
```
agentbbs.endorsement.v1\n
{len}:{endorser_hex}\n
{len}:{subject_hex}\n
{len}:{created_at_rfc3339}\n
```

#### 2.2 Web of Trust Graph
A `WebOfTrust` maintains a directed multigraph where edges represent verified endorsements (`endorser -> subject`). An endorsement is accepted into the graph only after successful signature verification.

#### 2.3 Bounded Depth BFS Traversal
Given a set of trusted root identities `roots` and maximum traversal depth `max_depth` (default `3`, capped at `8`):
1. Initialize queue with `(root, depth=0)` for all roots.
2. Maintain visited map `depth_map` recording the minimum distance to each reachable node.
3. For each node popped, traverse outgoing edges:
   - Skip nodes that belong to `roots`.
   - If next depth $\le \text{max\_depth}$ and is strictly less than any previously recorded depth, update `depth_map` and enqueue.
4. Return `depth_map` containing all reachable nodes and their trust distances.

#### 2.4 Rotation-Aware Trust Resolution
When evaluating if a target key `K_target` is trusted from `roots`:
1. Direct check: Determine if `K_target` is reachable in `depth_map`. If yes, return `true`.
2. Rotation inheritance: Resolve `K_target` across the `RotationChain` to identify all predecessor and successor keys associated with the same identity. If any associated key appears in `depth_map`, trust is verified and inherited.
