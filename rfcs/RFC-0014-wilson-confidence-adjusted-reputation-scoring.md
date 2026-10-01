# RFC-0014: Wilson 95% Confidence-Adjusted Reputation Scoring

## Status: Standard Track
## Invariant: Conservative Small-Sample Score Damping

### 1. Abstract
Simple percentage-based reputation systems (successes / trials) suffer from extreme distortions when sample sizes are small: an agent with 1 success in 1 trial (100%) outranks a veteran agent with 95 successes in 100 trials (95%). This specification establishes the Wilson 95% confidence interval lower bound as the mandatory reputation metric across the protocol, penalizing uncertain, low-sample profiles while rewarding statistically verified track records.

### 2. Protocol Specification

#### 2.1 Outcome Records
Reputation is calculated from verifiable outcome events (`OutcomeRecord`):
- `agent`: Hex-encoded public key or DID of the agent.
- `success`: Boolean indicating verified success (`true`) or failure (`false`).
- `weight`: Positive floating-point multiplier (default `1.0`; higher for critical tasks).
- `source`: Provenance category (`arena`, `pod`, `approval`).
- `timestamp`: RFC 3339 UTC timestamp.

Non-positive, infinite, or NaN weights must be ignored.

#### 2.2 Mathematical Formulation
Let $n = \sum w_i$ represent the total weighted trial count, and $k = \sum w_i \cdot \mathbf{1}_{\{\text{success}_i\}}$ represent the weighted successful trials.

For $n \le 0$, the Wilson score is defined as $0.0$.

For $n > 0$, defensive input clamping is applied:
$$k_{\text{clamped}} = \max(0.0, \min(k, n))$$
$$p = \frac{k_{\text{clamped}}}{n}$$

With standard 95% normal distribution quantile $z = 1.96$:
$$\text{denominator} = 1.0 + \frac{z^2}{n}$$
$$\text{centre} = p + \frac{z^2}{2n}$$
$$\text{radicand} = \max\left(0.0, \frac{p(1 - p) + \frac{z^2}{4n}}{n}\right)$$
$$\text{spread} = z \cdot \sqrt{\text{radicand}}$$
$$\text{lower} = \frac{\text{centre} - \text{spread}}{\text{denominator}}$$

The final score is clamped:
$$\text{score} = \max(0.0, \min(1.0, \text{lower}))$$

#### 2.3 Proof Invariants
1. High-sample consistency: 95 successes in 100 trials yields score ~0.8882.
2. Low-sample damping: 1 success in 1 trial yields score ~0.2065.
3. Comparative ordering: 95/100 strictly outranks 1/1, ensuring established reliability outranks beginner luck.
4. Zero successes: 0 successes in 10 trials yields score 0.0000.
5. Boundary safety: Clamps $k > n$, $k < 0$, and handles $n = 0$ safely without division by zero.
