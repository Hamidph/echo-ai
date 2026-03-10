---
name: experiment-report
description: Analyze and explain Echo AI brand visibility experiment results. Use when user says "analyze results", "generate report", "what do results show", "explain this experiment", "interpret visibility data", or shares experiment output data.
allowed-tools: Read, Bash
---

# Experiment Report Generator

Echo AI metrics reference:
- **Visibility Rate**: % of LLM responses that mention the brand
- **Share of Voice**: brand mentions ÷ total brand + competitor mentions
- **Average Position**: ordinal position of first brand mention in response
- **Consistency Score**: standard deviation across Monte Carlo iterations (lower = more stable)
- **Sentiment**: positive / neutral / negative classification of brand mentions
- **Hallucination Rate**: % of mentions containing factually incorrect claims
- **First Mention Rate**: % of responses where brand appears before competitors

For the data "$ARGUMENTS":

### Report output

**Executive Summary** (3 bullet points, plain English, no jargon)

**Metrics Table**

| Metric | Score | Benchmark | Status |
|---|---|---|---|
| Visibility Rate | | | 🟢/🟡/🔴 |
| Share of Voice | | | |
| Avg Position | | | |
| Consistency | | | |
| Sentiment | | | |
| Hallucination Rate | | | |
| First Mention Rate | | | |

**What's Working** (highest performing areas with interpretation)

**Red Flags** (anything below benchmark — especially high hallucination rate)

**Competitor Comparison** (if competitor data present)

**Top 3 Recommendations** (specific, actionable, prioritized)

**Prompt Optimization Suggestions** (rewrite the experiment prompts for better results)

Write for a brand manager or CMO — no technical jargon, focus on business impact.
