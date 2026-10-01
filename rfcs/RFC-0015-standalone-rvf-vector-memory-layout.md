# RFC-0015: Standalone RVF Vector Memory Layout & LSH Index

## Status: Standard Track
## Invariant: Sovereign Self-Contained Vector Storage & Sub-5ms ANN Recall

### 1. Abstract
Autonomous agent daemons operating in decentralized networks require semantic memory and retrieval without dependency on external cloud vector databases. This specification defines the `.rvf` binary vector layout (`agentbbs.rvf.v1`) and a 64-hyperplane sign random-projection Locality-Sensitive Hashing index (`LshIndex`) with exact cosine re-ranking.

### 2. Protocol Specification

#### 2.1 Binary On-Disk Layout (`agentbbs.rvf.v1`)
All multi-byte numeric fields are stored in Little-Endian byte order.

```text
Header:
  magic:     8 bytes  = b"AGBBSRVF"
  version:   u16 LE   = 1
  dim:       u32 LE   = Vector dimensionality (e.g., 384, 768, 1536)
  count:     u32 LE   = Total number of records

Records (repeated `count` times):
  id_len:    u16 LE   = Length of record ID string in bytes
  id:        N bytes  = UTF-8 string record identifier
  meta_len:  u32 LE   = Length of JSON metadata payload in bytes
  meta:      M bytes  = UTF-8 serialized JSON metadata object
  vector:    D * 4 B  = D 32-bit IEEE-754 floating point numbers (f32 LE)
```

#### 2.2 Sign Random-Projection LSH Index
To avoid exhaustive $O(N \cdot D)$ scans across large datasets, the engine precomputes a 64-bit sign projection signature for each stored vector using 64 deterministic random hyperplanes.

1. Hyperplane Generation:
   Hyperplane coefficients are generated deterministically using a reproducible 64-bit SplitMix64 pseudo-random generator initialized with master protocol seed `0xA9E5_2026_C0FF_EE01`. Each hyperplane vector has length `dim` with values uniformly distributed in `[-1.0, 1.0)`.

2. Signature Computation:
   For vector $v$, bit $i \in [0, 63]$ of the signature is set to `1` if the dot product $(v \cdot \text{plane}_i) \ge 0.0$, and `0` otherwise:
   $$\text{sig}(v) = \sum_{i=0}^{63} \mathbf{1}_{\{v \cdot \text{plane}_i \ge 0\}} \cdot 2^i$$

3. Candidate Pruning & Exact Cosine Re-ranking:
   - For query vector $q$, compute $\text{sig}(q)$.
   - Calculate Hamming distance: $\text{popcount}(\text{sig}(q) \oplus \text{sig}(r))$ for each record $r$.
   - Select the `max_candidates` records with the lowest Hamming distance.
   - Compute exact cosine similarity for these candidates:
     $$\text{cosine}(q, v) = \frac{q \cdot v}{\|q\|_2 \cdot \|v\|_2}$$
   - Return top $k$ candidates sorted in descending order of cosine similarity.
