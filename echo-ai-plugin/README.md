# Echo AI Tools Plugin

Engineering, marketing, product, and ops toolkit for **Echo AI** — an AI Search Analytics Platform that measures brand visibility across LLM-powered search engines using Monte Carlo simulations.

## Components

### Skills (auto-invoked when contextually relevant)

| Skill | Purpose |
|---|---|
| call-prep (experiment-report) | Analyze brand visibility experiment results |
| competitive-intelligence (competitor-analysis) | Research and analyze competitors |
| deal-strategy (pricing-review) | Review and optimize pricing strategy |
| customer-research (debug) | Debug errors and failures |
| code-review (review-pr) | Review code for quality and security |

### Commands (explicit slash commands)

| Command | Usage |
|---|---|
| `/echo-ai-tools:deploy` | Deploy to Railway production |
| `/echo-ai-tools:commit` | Smart commit with conventional format |
| `/echo-ai-tools:test` | Run test suites |
| `/echo-ai-tools:release` | Create versioned release |
| `/echo-ai-tools:standup` | Daily standup summary |
| `/echo-ai-tools:sprint-plan` | Plan development sprint |
| `/echo-ai-tools:db-query` | Query PostgreSQL (read-only) |
| `/echo-ai-tools:content-brief` | Create marketing content briefs |
| `/echo-ai-tools:launch-post` | Draft launch announcements |
| `/echo-ai-tools:customer-email` | Draft customer-facing emails |
| `/echo-ai-tools:api-docs` | Generate API documentation |
| `/echo-ai-tools:bug-report` | Create structured bug reports |
| `/echo-ai-tools:changelog` | Generate changelog from commits |
| `/echo-ai-tools:onboarding-doc` | Create onboarding documentation |

### Agents

| Agent | Purpose | Model |
|---|---|---|
| code-reviewer | Reviews code for quality, security, correctness | sonnet |
| debugger | Debugs errors in FastAPI, Celery, PostgreSQL, Redis, Next.js | sonnet |
| db-analyst | Read-only PostgreSQL queries for analytics and metrics | sonnet |
| marketing-researcher | Market research, competitor intel, content opportunities | sonnet |
| customer-success | Support issues, drafts responses, identifies churn risks | sonnet |

### Hooks

- **Branch protection**: Blocks pushes to main/master and destructive git commands
- **Auto-format**: Runs ruff (Python) or prettier (TS/JS) after file edits
- **Session reminder**: Shows Echo AI context banner on session start

### MCP Servers

| Server | Purpose |
|---|---|
| GitHub | PR management, issues, releases |
| Notion | Docs, roadmap, meeting notes |
| Sentry | Error monitoring |
| Stripe | Billing, customer data |
| Slack | Team communication |

## Setup

```bash
# Claude Code CLI
claude --plugin-dir ./echo-ai-plugin

# Or install from marketplace (when published)
claude plugin install echo-ai-tools
```

## Customization

See [CONNECTORS.md](./CONNECTORS.md) to swap default tools for your stack.
