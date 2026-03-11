# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user connects in that category. Plugins are tool-agnostic — they describe workflows in terms of categories rather than specific products.

## Connectors for this plugin

| Category | Placeholder | Included servers | Other options |
|---|---|---|---|
| Chat | `~~chat` | Slack | Microsoft Teams, Discord |
| Project tracker | `~~project tracker` | GitHub Issues | Linear, Jira, Asana |
| Error monitoring | `~~error monitor` | Sentry | Datadog, Bugsnag |
| Billing | `~~billing` | Stripe | Paddle, Chargebee |
| Docs | `~~docs` | Notion | Confluence, Google Docs |
| Database | `~~database` | PostgreSQL (Railway) | Supabase, PlanetScale |
