# AI Visibility Frontend Dashboard

Modern React/Next.js dashboard for the AI Visibility platform.

## Features

- 🔐 Authentication (Login, Register, Email Verification)
- 💳 Billing & Subscription Management (Stripe)
- 📊 Experiment Creation & Monitoring
- 📈 Real-time Analytics Dashboards
- 🎨 Modern UI with Tailwind CSS
- ⚡ Server-Side Rendering with Next.js 14
- 🔄 Data Fetching with TanStack Query
- 📱 Responsive Design

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: React 18 + Tailwind CSS
- **State**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **API**: Axios

## Getting Started

### Prerequisites

- Node.js 18+ (or use `uv` Python tooling)
- Backend API running at `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/               # Next.js 14 App Router
│   │   ├── (auth)/       # Auth pages (login, register)
│   │   ├── dashboard/    # Dashboard pages
│   │   └── layout.tsx    # Root layout
│   ├── components/       # React components
│   │   ├── ui/          # Reusable UI components
│   │   ├── auth/        # Auth-related components
│   │   └── dashboard/   # Dashboard components
│   ├── lib/             # Utilities
│   │   ├── api.ts       # API client
│   │   └── auth.ts      # Auth helpers
│   └── types/           # TypeScript types
├── public/              # Static assets
└── package.json
```

## Key Pages

- `/` - Landing page
- `/login` - User login
- `/register` - User registration
- `/verify-email` - Email verification
- `/dashboard` - Main dashboard
- `/dashboard/experiments` - Experiments list
- `/dashboard/experiments/new` - Create experiment
- `/dashboard/billing` - Billing & subscription
- `/dashboard/settings` - User settings

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## API Integration

The frontend communicates with the backend API at `/api/v1`:

- **Auth**: `/api/v1/auth/*`
- **Experiments**: `/api/v1/experiments/*`
- **Billing**: `/api/v1/billing/*`

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```bash
docker build -t ai-visibility-frontend .
docker run -p 3000:3000 ai-visibility-frontend
```

### Static Export

```bash
npm run build
# Deploy the `out/` directory to any static host
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

MIT
