# Contributing to Gateway El Salvador

Thank you for your interest in contributing to Gateway El Salvador! 🇸🇻

## Development Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/your-org/PupuserIA.git
   cd PupuserIA
   ```

2. **Install dependencies:**
   ```bash
   pnpm install              # Frontend & monorepo
   cd apps/api && uv venv && uv pip install -r requirements.txt  # Backend
   ```

3. **Start infrastructure:**
   ```bash
   docker compose up postgres redis meilisearch -d
   ```

4. **Run in development:**
   ```bash
   pnpm dev  # Starts all services via Turborepo
   ```

## Branching Strategy

- `main` — Production-ready code
- `develop` — Integration branch
- `feat/*` — Feature branches
- `fix/*` — Bug fix branches
- `docs/*` — Documentation updates

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add property search filters
fix: correct AI valuation confidence calculation
docs: update API endpoint documentation
chore: upgrade Next.js to 15.2
```

## Code Quality

- **TypeScript:** Strict mode enabled
- **Python:** Ruff for linting, mypy for type checking
- **Go:** Standard `go vet` and `golint`
- **All:** Pre-commit hooks via Husky + lint-staged

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Ensure CI passes (`pnpm lint && pnpm test && pnpm typecheck`)
4. Open a PR with a clear description
5. Get at least one review
6. Squash merge to `main`

## Foundation Layer

The Foundation components (AI Tutor, impact tracking) are dual-licensed under MIT
to maximize adoption. Contributions to education tools are especially welcome.

## Questions?

Open an issue or reach out to the team. We're building this together. 🤝
