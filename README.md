# 🇸🇻 Gateway El Salvador — PupuserIA

> *Built with AI. Funded by the world. For the children of El Salvador.*

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-black?logo=github)](/.github/workflows)
[![Next.js 15](https://img.shields.io/badge/Frontend-Next.js%2015-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Go](https://img.shields.io/badge/Services-Go-00ADD8?logo=go)](https://go.dev/)
[![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL%20%2B%20PostGIS-4169E1?logo=postgresql)](https://www.postgresql.org/)

---

## 🌎 What is Gateway El Salvador?

An **AI-powered, full-stack platform** that serves as the definitive digital gateway to El Salvador — combining immersive content, tourism commerce, real estate investment tools, and diaspora financial services into a single ecosystem.

**The core equation:**

```
Outside Money (Tourism + Investment + Diaspora)
        ↓
   [Gateway El Salvador Platform]
        ↓
   Revenue Generated
        ↓
   10-20% → Foundation
        ↓
   AI Tutoring + Meals + Devices + Energy + Supplies
        ↓
   Children with equal opportunity
        ↓
   Educated workforce → Stronger economy → More investment
        ↓
   ♻️ Virtuous Cycle
```

---

## 🏗️ Architecture Overview

Gateway El Salvador is organized as a **monorepo** with clearly separated concerns:

```
PupuserIA/
├── apps/
│   ├── web/                    # Next.js 15 frontend (TypeScript)
│   ├── api/                    # FastAPI backend (Python)
│   └── services/               # Go microservices
│       ├── payments/           #   Stripe + Lightning payment processing
│       ├── bookings/           #   Tour & rental booking orchestration
│       └── pricing/            #   Real-time pricing engine
├── packages/
│   ├── ui/                     # Shared React component library
│   ├── types/                  # Shared TypeScript type definitions
│   ├── config/                 # Shared ESLint, Tailwind, TS configs
│   └── database/               # Prisma schema & migrations
├── ai/
│   ├── valuation/              # Property valuation engine (PyTorch + XGBoost)
│   ├── concierge/              # RAG-powered AI concierge (Claude API)
│   ├── content/                # SEO content generation pipeline
│   └── tutor/                  # Edge AI tutoring models (ONNX/GGUF)
├── foundation/
│   ├── dashboard/              # Public impact transparency dashboard
│   ├── contracts/              # Blockchain impact tracking (Stellar/Polygon)
│   └── programs/               # Nutrition, devices, energy program management
├── infra/
│   ├── docker/                 # Docker Compose & Dockerfiles
│   ├── terraform/              # AWS infrastructure as code
│   └── k8s/                    # Kubernetes manifests (future)
├── data/
│   ├── scrapers/               # ES listing & cadastral data scrapers
│   ├── pipelines/              # ETL pipelines for data ingestion
│   └── seeds/                  # Database seed data
├── docs/                       # Architecture docs, ADRs, API specs
├── .github/
│   └── workflows/              # CI/CD pipelines
├── docker-compose.yml          # Local development environment
├── turbo.json                  # Turborepo pipeline configuration
└── package.json                # Monorepo root
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15 (TypeScript), Tailwind CSS v4, Mapbox GL JS, Deck.gl | SSR/ISR content, interactive maps, booking flows |
| **Backend API** | FastAPI (Python 3.12+), Pydantic v2 | AI inference orchestration, bilingual content, WebSocket chat |
| **Backend Services** | Go 1.22+ | Payment processing, booking orchestration, real-time pricing |
| **AI — Valuation** | XGBoost, scikit-learn, NumPy | Property price estimation (trained on 12 scraped sources incl. bank foreclosures) |
| **AI — Concierge** | Claude API, LangChain, Pinecone/Weaviate | RAG chatbot over proprietary ES knowledge base |
| **AI — Content** | Claude API, custom prompts | Automated SEO content generation (EN/ES) |
| **AI — Education** | ONNX Runtime, llama.cpp, GGUF models | Offline-first AI tutoring on edge devices |
| **Database** | PostgreSQL 16 + PostGIS | Geospatial queries, property data, user data |
| **Search** | Meilisearch | Typo-tolerant bilingual full-text search |
| **Cache** | Redis 7 | Sessions, rate limiting, real-time pricing cache |
| **Payments** | Stripe, Bitcoin Lightning (LND) | Fiat + BTC payment processing |
| **Impact Tracking** | Stellar / Polygon | On-chain fund allocation transparency |
| **Infrastructure** | Vercel (frontend), AWS (backend, AI), Docker | Global CDN, GPU inference, containerized services |
| **Observability** | Prometheus, Grafana, Sentry | Metrics, dashboards, error tracking |
| **CI/CD** | GitHub Actions, Docker, Turborepo | Automated testing, builds, preview deploys |

---

## 🧩 Platform Layers

### Layer 1 — The Window (Content & Discovery)
- 🗺️ Interactive country map (14 departments, every municipio)
- 🤖 AI trip planner with bilingual chatbot
- 📊 Safety dashboard with real-time data visualization
- ₿ Bitcoin & expat comprehensive guides
- ✍️ AI-powered SEO content engine

### Layer 2 — The Marketplace (Commerce & Investment)
- 🏄 Tour & experience booking with instant confirmation
- 🏠 Property marketplace with AI valuations & 3D tours
- 💸 Diaspora investment portal (from $150/month)
- 📞 $200/hr investor consulting with AI briefing packets
- 🔍 AI-powered property matching & rental yield projections

### Layer 3 — The Foundation (Impact & Reinvestment)
- 🎓 AI tutoring network on edge devices for rural schools
- 🍽️ Nutrition program partnerships
- 💻 Laptops, tablets & solar chargers for students
- ⚡ Solar microgrid installations
- 📊 Public blockchain-verified impact dashboard

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 20+ & **pnpm** 9+
- **Python** 3.12+ & **uv** (or pip)
- **Go** 1.22+
- **Docker** & **Docker Compose**
- **PostgreSQL** 16 (or use Docker)
- **Redis** 7 (or use Docker)

### Quick Start (Docker — Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/PupuserIA.git
cd PupuserIA

# Copy environment files
cp .env.example .env

# Start all services
docker compose up -d

# Seed the database
pnpm db:seed

# Open the app
open http://localhost:3000
```

### Manual Setup

```bash
# 1. Install monorepo dependencies
pnpm install

# 2. Set up Python backend
cd apps/api
uv venv
uv pip install -r requirements.txt

# 3. Set up Go services
cd apps/services/payments
go mod download

# 4. Start PostgreSQL + Redis (Docker)
docker compose up postgres redis meilisearch -d

# 5. Run database migrations
pnpm db:migrate

# 6. Start all services in development
pnpm dev
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gateway_es
REDIS_URL=redis://localhost:6379

# AI
ANTHROPIC_API_KEY=sk-ant-...
PINECONE_API_KEY=...

# Payments
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Maps
NEXT_PUBLIC_MAPBOX_TOKEN=pk....

# Meilisearch
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=...
```

---

## 📅 Implementation Roadmap

| Phase | Name | Timeline | Milestone |
|-------|------|----------|-----------|
| **V0** | The Landing | Weeks 1-2 | Landing page, 10 guides, 1K email subscribers |
| **V1** | Marketplace MVP | Weeks 3-5 | First $1K revenue: tours, consulting, property referrals |
| **V2** | Valuation Engine | Weeks 6-8 | 200+ properties, AI valuations within 15% accuracy |
| **V3** | The Foundation | Weeks 9-10 | First school receiving AI tutoring, impact dashboard live |
| **V4** | Scale Engine | Weeks 11-12 | 10K monthly visitors, $5K/mo revenue, 3 schools |
| **V5** | Rental Empire | Month 4-6 | 50 managed properties, $15K/mo recurring |
| **V6** | Diaspora Engine | Month 6-9 | 200 active investors, $50K/mo capital flow |
| **V7** | Education Network | Month 9-12 | 5,000 students with AI tutoring |
| **V8** | Country OS | Month 12+ | Definitive platform for El Salvador |

---

## 📊 Market Opportunity

| Metric | Value |
|--------|-------|
| ES Tourism Revenue (2025) | ~$4.2B |
| Tourism as % of GDP | 14.5% and rising |
| Annual Tourist Arrivals | 4M+ |
| Diaspora Remittances | $10B/year (25% of GDP) |
| Real Estate as % of GDP | 9% and rising |
| AI Innovation Tax Rate | 0% (ES AI Law 2025) |
| Existing MLS / Dominant Platform | **None** |
| Real Estate Licensing Required | **No** |
| Children Not Finishing 6th Grade | >50% |

---

## 💰 Revenue Streams

| Stream | Margin | Recurring | Go-Live |
|--------|--------|-----------|---------|
| Tour Commissions (15-20%) | High | Per-booking | Month 1 |
| Consulting ($200/hr) | Very High | Per-session | Month 1 |
| Property Referrals (25-30%) | High | Per-sale | Month 2 |
| Featured Listings ($50-200/mo) | Very High | Monthly | Month 3 |
| Rental Management (15-20%) | Medium | Monthly | Month 4 |
| Property Sales (3-5%) | Very High | Per-sale | Month 6 |
| AI Subscription ($9.99/mo) | Very High | Monthly | Month 6 |
| Diaspora Platform Fees (1-2%) | Medium | Per-tx | Month 8 |

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **AGPL-3.0 License** — see [LICENSE](LICENSE) for details.

The Foundation layer components are additionally licensed under **MIT** to enable maximum community adoption for educational tools.

---

## 🙏 Acknowledgments

- The children of El Salvador who deserve every opportunity
- The Salvadoran diaspora whose remittances sustain families
- The open-source community whose tools make this possible

---

<p align="center">
  <strong>Gateway El Salvador</strong><br>
  <em>The sovereign platform for a nation's transformation.</em><br><br>
  🇸🇻 Hecho con amor para El Salvador 🇸🇻
</p>
