# Echo AI - Complete Website Sitemap & Feature Documentation

**Last Updated**: January 1, 2026
**Environment**: Development (Testing Mode Enabled)

---

## 🗺️ Site Architecture

```
Echo AI Platform
│
├── 🏠 Public Pages (Unauthenticated)
│   ├── / (Landing Page)
│   ├── /login
│   └── /register
│
├── 🔐 Application Pages (Authenticated)
│   ├── /dashboard
│   ├── /experiments
│   ├── /experiments/new
│   ├── /experiments/[id]
│   └── /settings
│
└── 📡 API Endpoints (Backend)
    ├── /health
    ├── /api/v1/docs
    └── /api/v1/* (see API section below)
```

---

## 📄 Page-by-Page Breakdown

### 1. **Landing Page** (`/`)
**Purpose**: Marketing homepage to attract and convert visitors

**Sections**:
- Hero section with animated stats and gradient design
- Value propositions: Visibility, Position, Sentiment metrics
- Mock dashboard preview (visual demo)
- Feature highlights grid
- Social proof (testimonials, company logos)
- Pricing tiers preview
- CTA buttons: "Start Free Trial" → /register

**Key Metrics Shown** (Marketing Copy):
- 50K+ prompts tracked (dummy)
- 1,500+ marketing teams (dummy)
- 3 AI models supported
- 99% accuracy claim (dummy)

**Technologies**: Next.js, Tailwind CSS, glassmorphism effects

---

### 2. **Login Page** (`/login`)
**Purpose**: User authentication

**Features**:
- Email + Password form
- "Remember me" checkbox
- "Forgot password?" link (not yet implemented)
- Demo credentials display for testing
- Glassmorphic card design with cyan-violet gradient
- Background: animated gradient orbs + grid pattern

**Authentication Flow**:
1. Submit credentials → `/api/v1/auth/login`
2. Receive JWT tokens (access + refresh)
3. Store access_token in localStorage
4. Redirect to `/dashboard`

**Demo Credentials**:
- Email: demo@example.com
- Password: demo123

---

### 3. **Register Page** (`/register`)
**Purpose**: New user account creation

**Form Fields**:
- Full Name
- Email address
- Password (with validation)
- Confirm Password

**Features**:
- Shows benefits:
  - 100 free prompts/month
  - No credit card required
  - Cancel anytime
- Same glassmorphic design as login
- Auto-redirects to /login?registered=true on success

**Account Creation**:
- Creates FREE tier account
- Monthly quota: 100 prompts (1000 iterations max)
- Quota resets monthly
- Email verification (sent but not enforced)

---

### 4. **Dashboard** (`/dashboard`)
**Purpose**: Main analytics overview

**Layout**:
```
Header: Welcome, [User Name]!
│
├── Top Metrics Row (3 cards)
│   ├── Visibility: XX% (+/- change)
│   ├── Sentiment: XX/100 (+/- change)
│   └── Position: #X (+/- change)
│
├── Main Content (2 columns)
│   ├── Left: 12-month trend chart
│   │   └── Bar chart showing visibility over time
│   ├── Right: Competitor comparison
│   │   └── Horizontal bars for brand rankings
│
└── Sidebar (Right)
    ├── Usage Stats
    │   ├── Prompts used: X/100
    │   ├── Remaining: XX
    │   └── Next reset: [date]
    ├── Quick Actions
    │   ├── New Analysis button
    │   └── View History button
    └── Recent Analyses (last 3)
```

**Data Sources**:
- Real experiment results from database
- Aggregated metrics calculated from experiments
- **Note**: Currently may show dummy data - needs real experiments

**Interactive Elements**:
- Metric cards are tabs (click to switch views)
- Chart hover tooltips
- Competitor bars are clickable

---

### 5. **Experiments List** (`/experiments`)
**Purpose**: View all experiments with search/filter

**Features**:
- Table view with columns:
  - Prompt (truncated)
  - Target Brand
  - Provider (ChatGPT/Perplexity/Claude)
  - Status (completed/running/failed/pending)
  - Created date
  - Actions (View button)

**Filters**:
- All / Completed / Running / Failed (tabs)
- Search bar (searches prompts)

**Status Indicators**:
- Completed: Green badge
- Running: Cyan badge with pulse animation
- Failed: Red badge
- Pending: Amber badge

**Pagination**: 10 results per page

**Empty State**: Shows when no experiments exist
- Message: "No experiments yet"
- CTA: "Create your first experiment"

---

### 6. **Create Experiment** (`/experiments/new`)
**Purpose**: Run new AI visibility analysis

**Multi-Step Form**:

**Step 1: Query Configuration**
- Prompt text (textarea, required)
  - Example: "What are the best CRM tools for startups?"
- Target Brand (text input, required)
  - Example: "Salesforce"
- Competitor Brands (optional, comma-separated)
  - Example: "HubSpot, Pipedrive, Zoho"
- Domain Whitelist (optional, for citation filtering)

**Step 2: AI Provider Selection**
- Radio buttons:
  - ☑️ ChatGPT (OpenAI)
  - ☐ Perplexity
  - ☐ Claude (Anthropic)
- Model selection (auto-fills):
  - ChatGPT: **gpt-4o** (same as ChatGPT UI)
  - Perplexity: sonar-pro
  - Claude: claude-3-5-sonnet

**Step 3: Configuration**
- Number of iterations: 10 (fixed for now)
  - Info tooltip: "Each prompt runs 10 iterations for statistical significance"
- Temperature: 0.7 (slider, 0.0-1.0)
- System prompt (optional, advanced)

**Step 4: Review & Submit**
- Shows summary of all selections
- Cost estimate: "This will use 1 prompt from your quota"
- "Run Analysis" button

**Quota Handling**:
- **Testing Mode (Current)**: Unlimited prompts
- **Production Mode**: Checks prompts_used_this_month < monthly_prompt_quota
- Shows warning if quota low

**Submission Flow**:
1. POST to `/api/v1/experiments`
2. Returns experiment_id and job_id (Celery task)
3. Redirects to `/experiments/[id]`
4. Background task starts executing

---

### 7. **Experiment Details** (`/experiments/[id]`)
**Purpose**: View results of a specific experiment

**Status Banner** (top):
- Pending: "Queued for execution..."
- Running: "Running iteration X/10..." (polls every 5s)
- Completed: "Completed" with timestamp
- Failed: "Failed" with error message

**Tabs**:

**Tab 1: Results** (when completed)
```
Provider: ChatGPT (gpt-4o)
Iterations: 10
Confidence: 95%

Brand Visibility:
├── [Target Brand]: XX% (confidence interval: XX%-XX%)
├── Competitor 1: XX%
└── Competitor 2: XX%

Mention Counts:
├── [Target Brand]: X/10
├── Competitor 1: X/10

Sentiment (if analyzed):
└── Overall Score: XX/100
```

**Tab 2: Details**
- Full experiment configuration
- Prompt text
- All parameters
- Metadata (created_at, updated_at, user_id)
- Raw API responses (collapsed, for debugging)

**Actions**:
- Download JSON (export results)
- Re-run Analysis (creates new experiment with same config)
- Share (copy link)

**Polling**: Auto-refreshes every 5 seconds while status = "running"

---

### 8. **Settings Page** (`/settings`)
**Purpose**: Account management and configuration

**Tabs**:

**Profile**:
- Full Name (editable)
- Email (read-only, contact support to change)
- Company (editable)
- Save/Cancel buttons

**Security**:
- Change Password form
  - Current password
  - New password
  - Confirm new password
- Two-Factor Authentication
  - Status: Not enabled
  - "Enable 2FA" button (not yet implemented)

**Billing**:
- Current Plan card:
  - Plan name (FREE/STARTER/PRO/ENTERPRISE)
  - Monthly quota: X prompts
  - "Upgrade Plan" button (if FREE)
- Usage Stats (3 cards):
  - Prompts Used: X
  - Remaining: X
  - Reset Date: [date]
- Cancel Subscription button (if paid plan)

**Notifications**:
- Toggle switches for:
  - ✓ Experiment Completion (email when done)
  - ✓ Visibility Alerts (significant drops)
  - ✓ Weekly Reports (Sunday summary)
  - ✓ Product Updates (new features)

**API Keys**:
- List of generated API keys
- Each key shows:
  - Name/Label
  - Created date
  - Status badge (Active/Revoked)
  - Masked key: `sk_live_••••••••••••••••`
  - Copy / Revoke buttons
- "Generate New API Key" button

---

## 🔌 API Endpoints Reference

### Authentication (`/api/v1/auth`)
```
POST   /auth/register          Create new account
POST   /auth/login             Login (returns JWT)
POST   /auth/refresh           Refresh access token
GET    /auth/me                Get current user info
POST   /auth/verify-email/{token}     Verify email
POST   /auth/resend-verification      Resend verification
POST   /auth/forgot-password          Request password reset
POST   /auth/reset-password/{token}   Reset password
POST   /auth/api-keys          Create API key
GET    /auth/api-keys          List user's API keys
DELETE /auth/api-keys/{id}     Revoke API key
```

### Experiments (`/api/v1/experiments`)
```
POST   /experiments            Create new experiment
GET    /experiments            List experiments (paginated)
GET    /experiments/{id}       Get experiment status & results
GET    /experiments/{id}/details       Get full details
GET    /experiments/{id}/report        Get visibility report
```

### Billing (`/api/v1/billing`)
```
GET    /billing/pricing-tiers          Get available plans
POST   /billing/create-checkout-session    Start Stripe checkout
GET    /billing/subscription           Get user subscription
POST   /billing/cancel-subscription    Cancel paid plan
```

### System
```
GET    /health                 Health check (Basic)
GET    /api/v1/health/detailed Detailed Health (DB + Redis)
GET    /api/v1/docs            Swagger UI docs
```

### Demo (Public)
```
POST   /api/v1/demo/quick-analysis   Run quick demo (5 iterations)
```

---

## 📊 Key Metrics Explained

### Visibility
**Definition**: Percentage of AI responses that mention your brand

**Calculation**:
- Run prompt 10 times (iterations)
- Count how many responses mention target brand
- Visibility = (mentions / total iterations) × 100

**Example**:
- 10 iterations
- Brand mentioned in 7 responses
- Visibility = 70%

**Confidence Interval**: 95% CI shows statistical range
- Example: 70% ± 15% means true visibility is likely between 55%-85%

### Position
**Definition**: Average ranking position when brand is mentioned

**Calculation**:
- For each response, find order of brand mentions
- Average the positions where target brand appears
- Lower number = better (closer to #1)

**Example**:
- Response 1: Target brand mentioned 2nd
- Response 2: Target brand mentioned 1st
- Response 3: Target brand mentioned 3rd
- Average Position = #2

### Sentiment
**Definition**: Quality of how AI describes your brand (0-100 scale)

**Calculation** (planned):
- Analyze tone of mentions
- Score: Positive (80-100), Neutral (40-79), Negative (0-39)
- Average across all mentions

**Currently**: Not fully implemented, shows placeholder

---

## 🎯 User Journey (Happy Path)

1. **Discover** → Land on homepage, see value prop
2. **Sign Up** → /register, create FREE account (100 prompts)
3. **Onboard** → First login shows 6-step interactive tour
4. **Explore** → View dashboard (empty state or demo data)
5. **Create** → /experiments/new
   - Enter: "Best project management tools"
   - Target: "Asana"
   - Competitors: "Monday.com, Trello"
   - Provider: ChatGPT (gpt-4o)
6. **Wait** → /experiments/[id] shows "Running..." (30-60 seconds)
7. **Analyze** → Results tab shows:
   - Asana: 60% visibility
   - Monday.com: 40%
   - Trello: 30%
8. **Compare** → Dashboard updates with new data
9. **Iterate** → Create more experiments to track trends
10. **Upgrade** → Hit quota limit, upgrade to paid plan

---

## 🚧 Currently In Testing Mode

**Active Settings**:
- `TESTING_MODE=true`
- `UNLIMITED_PROMPTS=true`
- No quota enforcement
- Full access to all features

**For Production**:
- Set `TESTING_MODE=false`
- Remove `UNLIMITED_PROMPTS` or set to `false`
- Enforce: `prompts_used_this_month < monthly_prompt_quota`

---

## 🔧 Technical Stack

**Frontend**:
- Next.js 14 (App Router)
- React 18 with hooks
- Tailwind CSS (custom design system)
- React Query (data fetching)
- React Hot Toast (notifications)

**Backend**:
- FastAPI (Python 3.14)
- SQLAlchemy 2.0 (async ORM)
- PostgreSQL 15
- Redis (caching + Celery broker)
- Celery (background tasks)

**AI Providers**:
- OpenAI (gpt-4o)
- Anthropic (claude-3-5-sonnet)
- Perplexity (sonar-pro)

**Auth**:
- JWT (15min access + 7day refresh tokens)
- Bcrypt password hashing
- Optional 2FA (not yet implemented)

---

## 📝 Data Flow Example

**Create Experiment**:
```
User (Frontend)
  ↓ POST /api/v1/experiments
FastAPI Router
  ↓ validates request
  ↓ checks quota (skipped in testing mode)
  ↓ creates Experiment record (status: pending)
  ↓ queues Celery task
  ↓ returns {experiment_id, job_id}
  ↓
Celery Worker (background)
  ↓ picks up task
  ↓ for i in range(10):
  ↓   → calls OpenAI API (gpt-4o)
  ↓   → saves iteration result
  ↓ calculates visibility metrics
  ↓ updates experiment (status: completed)
  ↓
User (Frontend)
  ↓ polls GET /experiments/{id} every 5s
  ↓ sees status change to "completed"
  ↓ displays results
```

---

## 🎨 Design System

**Color Palette**:
- Background: #030712 (dark navy)
- Cards: #0a0f1a (slate)
- Primary: Cyan (#22d3ee) → Violet (#8b5cf6) gradient
- Success: Emerald (#10b981)
- Warning: Amber (#f59e0b)
- Error: Rose (#f43f5e)

**Typography**:
- Display: Syne (headings)
- Body: Outfit (sans-serif)

**Components**:
- Glassmorphism cards (backdrop-blur)
- Gradient buttons with hover scale
- Pulse animations for "running" states
- Tooltips for metric explanations

---

## 📦 Component Library

**Location**: `/frontend/src/components/ui/`

- **Button**: 5 variants, 3 sizes, loading states
- **Card**: Modular with Header/Content/Footer
- **Badge**: Status-aware color coding
- **Input**: With labels, errors, icons
- **Tooltip**: 4 positions, delay config

**Usage**:
```tsx
import { Button, Card, Badge, Input, Tooltip } from '@/components/ui';
```

---

## 🔮 Planned Features (Not Yet Implemented)

- [ ] Email verification enforcement
- [ ] Password reset flow
- [ ] Two-factor authentication
- [ ] Stripe payment integration (checkout works, webhooks needed)
- [ ] Export to CSV/PDF
- [ ] Scheduled experiments (cron)
- [ ] Slack/Email notifications
- [ ] Team collaboration
- [ ] White-label API
- [ ] Advanced analytics (time series)
- [ ] Sentiment analysis (full implementation)
- [ ] Citation tracking
- [ ] Geographic insights

---

This sitemap provides a complete reference for navigating and understanding Echo AI. All pages are live and accessible at http://localhost:3000 (frontend) and http://localhost:8000 (API).
