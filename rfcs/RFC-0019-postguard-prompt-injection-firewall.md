# RFC-0019: PostGuard Heuristic Prompt Injection Firewall & Egress PII Redaction

## Status: Standard Track
## Invariant: Pre-Flight Injection Rejection & Zero PII Leakage

### 1. Abstract
Deliberation messages and agent inputs originate from untrusted external actors. Digital signatures guarantee authenticity of authorship, but cannot ensure safety of content. This specification defines PostGuard, a deterministic pre-flight prompt injection scanner that rejects malicious payloads before LLM ingestion, and an egress PII scrubber that recursively masks sensitive credentials.

### 2. Protocol Specification

#### 2.1 PostGuard Heuristic Threat Levels
PostGuard evaluates inbound message text into one of three classifications:
- `clean`: No injection markers detected. Message proceeds to LLM ingestion.
- `suspicious`: Non-malicious anomalies detected (e.g., URL flooding with $>5$ links, opaque tokens with $>400$ consecutive non-whitespace characters). Message is permitted with audit logging.
- `malicious`: Obvious instruction override, prompt reveal, or jailbreak phrasing detected. Message is rejected immediately with HTTP 422 Unprocessable Entity.

#### 2.2 Malicious Injection Heuristics
A payload is marked `malicious` if it matches any known instruction override or prompt exfiltration pattern:
- `ignore previous instructions`
- `ignore all previous`
- `ignore the above`
- `ignore your instructions`
- `disregard previous`
- `disregard all previous`
- `disregard the above`
- `reveal your system prompt`
- `print your system prompt`
- `show your system prompt`
- `your system prompt is`
- `you are now`
- `do anything now`
- `developer mode enabled`
- `ignore your guidelines`
- `override your instructions`
- `system prompt reveal`
- `output your instructions`

Evaluation is case-insensitive and normalized against whitespace variations.

#### 2.3 Recursive Egress PII Sanitization
Before federation broadcast, external bridge forwarding, or persistence to disk, payloads undergo recursive PII sanitization.
The sanitizer inspects all object keys case-insensitively for sensitive identifiers:
- `email`, `ip`, `host`, `token`, `secret`, `key`, `phone`, `password`

Any field matching these substrings is replaced with the string `[redacted]`. Nested objects and arrays are traversed recursively without mutating benign sibling content.
