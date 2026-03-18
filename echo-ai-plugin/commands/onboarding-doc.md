---
description: Create onboarding documentation
allowed-tools: Read, Glob, Write
argument-hint: "<user|developer|team-member>"
---

# /onboarding-doc

Audience: $ARGUMENTS (default: user)

Read existing docs, routes, and README first before writing anything.

### New User Onboarding Guide
1. What is Echo AI (1 sentence + 1 sentence of why it matters)
2. Create your first experiment (step-by-step)
3. Understand your results (explain each metric in plain English)
4. Set up competitor tracking
5. Schedule recurring experiments
6. Export your data (CSV/JSON)
7. FAQ: top 5 support questions with answers

### Developer / API Quickstart
1. Get your API key (Settings → API Keys)
2. Create an experiment (curl + Python + Node examples)
3. Poll for results (async pattern with webhooks)
4. Rate limits and quotas by plan
5. Error codes reference

### New Team Member Setup
1. Read CLAUDE.md first
2. Clone repo and install dependencies
3. Set up .env (copy from .env.example, get values from Hamid)
4. Start local dev: `docker-compose up`
5. Run tests to confirm setup
6. Railway access: ask Hamid to add you

Simple language. Show don't tell. Copy-pasteable code in every example.
