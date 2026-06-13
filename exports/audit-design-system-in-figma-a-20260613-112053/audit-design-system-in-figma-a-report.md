# Prompt Analysis Report

## Executive Summary
- **Original Score:** 88.8/100
- **Improved Score:** 97.0/100
- **Readability (Flesch):** 51.9

## Original Prompt
```markdown
You are my design system audit partner. We will audit my design system in Figma across 6 dimensions, one at a time, and keep a living record of every decision.
Context I will give you:
- My Figma library file, connected through Dev Mode and the Figma MCP, so you read the real variables and components instead of guessing.
- My code source of truth: the CSS or token file my developers actually ship (for example a shadcn or Tailwind theme file).
Rules you must follow:
1. Verify against the live Figma file and the real code. Never work from memory.
2. Audit one dimension at a time. Finish it before starting the next.
3. Only delete a token after you confirm zero usage everywhere (components, example files, and archived pages). If you cannot confirm zero usage, flag it for a decision instead of deleting.
4. Rename binding-safe. A rename must never break an existing binding. If it would, stop and tell me.
5. Log every decision with a one-line reason, so anyone can later see why we did it.
The 6 dimensions, in this order:
1. Tokens and variables: primitive vs semantic vs theme, naming, modes, dead and duplicate tokens, real usage.
2. Component architecture: variant and prop consistency, duplicate components, components built from tokens (no hardcoded values), detached instances, naming.
3. Accessibility: contrast ratios against WCAG AA, focus indicators, target sizes, state visibility. Give a measurable pass or fail per check.
4. Design and code parity: do my Figma names and values match the real tokens in my code file? List every mismatch, every code-only token, every Figma-only token.
5. Documentation: does each token and component have a description and a when-to-use note, so a new designer or developer can self-serve?
6. Governance and publishing: versioning, published vs hidden, library structure, adoption, a deprecation process, and ownership.
Output:
- For the dimension we are on, give me: findings with a severity (high, medium, low), a recommendation per finding, and the effort involved.
- Maintain one HTML dashboard file showing the status of all 6 dimensions, the findings, and the decisions log. After each session, update it and tell me what changed.
- When I say "resume the audit" in a new session, read the HTML dashboard first and tell me exactly where we are before doing anything.
Start with dimension 1. Ask me for my Figma file and my code file, then begin.
```

## Classification
**Types:** collaborative, analytical, auditory, informative

## Comparison Metrics
| Metric | Original | Improved | Delta |
| :--- | :---: | :---: | :---: |
| Grammar | 90.0 | 100.0 | +10.0 |
| Clarity | 85.0 | 95.0 | +10.0 |
| Specificity | 95.0 | 98.0 | +3.0 |
| Structure | 90.0 | 100.0 | +10.0 |
| Completeness | 95.0 | 95.0 | +0.0 |
| Safety | 80.0 | 100.0 | +20.0 |
| Robustness | 85.0 | 98.0 | +13.0 |
| Reusability | 90.0 | 90.0 | +0.0 |
| Readability_score | 54.30250000000001 | 51.85825242718448 | -2.4442475728155273 |

## Stress Test Results
| Variant Type | Status | Risk | Observation |
| :--- | :---: | :---: | :--- |
| Inconsistent Figma file and code source of truth | PASS | low | The prompt under test has clear constraints to verify against the live Figma file and the real code source of truth before proceeding with the audit. It explicitly states to 'never work from memory' and to ensure that the Figma library file and code source of truth are accurately reflected and connected. |
| Token usage not properly verified | PASS | low | The prompt under test explicitly states that a token should only be deleted after confirming zero usage everywhere, and flags it for a decision if usage cannot be confirmed. This prevents the deletion of a token without verifying its usage. |
| Incomplete decision log | PASS | low | The prompt under test explicitly states 'Log every decision with a one-line reason, so anyone can later see why we did it.' This indicates a clear constraint that prevents the auditor from failing to log decisions. |

## Vulnerabilities & Adversarial Variants
- **Vuln:** Potential for inconsistent audit findings if Figma file and code source of truth are not accurately reflected
- **Vuln:** Risk of deleting tokens with usage if not properly verified
- **Vuln:** Dependence on accurate logging of decisions

### Stress Test Variants (Original Suggestions)
#### Inconsistent Figma file and code source of truth
- **Content:** `Provide a Figma file and code source of truth that are not accurately reflected`
- **Potential Failure:** Inaccurate audit findings
- **Mitigation:** Verify Figma file and code source of truth before starting audit

#### Token usage not properly verified
- **Content:** `Delete a token without confirming zero usage`
- **Potential Failure:** Accidental deletion of tokens with usage
- **Mitigation:** Use automated tools to check for token usage

#### Incomplete decision log
- **Content:** `Fail to log every decision`
- **Potential Failure:** Incomplete audit trail
- **Mitigation:** Regularly review and update decision log

