# Vinted Optimizer Enterprise

> Sistema enterprise per ottimizzare vendite su Vinted.it

## 🎯 Panoramica

Vinted Optimizer è un'applicazione completa per gestire e ottimizzare le vendite su Vinted, progettata per funzionare con budget minimo (€0-15/mese) su un iMac 2012.

### Funzionalità Principali
- 📸 **Analisi immagini AI** - Identificazione automatica prodotti e suggerimento prezzi
- 📊 **Dashboard centralizzata** - Gestione vendite multi-utente (familiari)
- 🚚 **Spedizioni integrate** - Multi-corriere con tracking
- 🤖 **Chatbot assistente** - Supporto interno con AI locale
- 📈 **Trend analysis** - Scraping dati di mercato Vinted

## 🏗️ Architettura

```
services/
├── api/              → FastAPI Python 3.12 (Fly.io)
├── frontend/         → Next.js 14 TypeScript (Cloudflare Pages)
├── ai-service/       → Ollama + moondream2 (locale iMac :8001)
├── scraper-service/  → curl-cffi + Playwright (locale iMac :8002)
└── worker/           → ARQ async workers (Fly.io)
```

## ⚡ Quick Start

### Prerequisiti
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- uv package manager (`pip install uv`)

### Setup Locale

1. **Clona il repository**
```bash
git clone https://github.com/yourusername/vinted-optimizer.git
cd vinted-optimizer
```

2. **Avvia database e Redis**
```bash
docker compose up -d
```

3. **Setup Backend API**
```bash
cd services/api
cp .env.example .env
# Modifica .env con le tue configurazioni

# Installa dipendenze
uv venv
source .venv/bin/activate  # Linux/macOS
uv pip install -e ".[dev]"

# Avvia server
uv run fastapi dev src/main.py --port 8000
```

4. **Verifica**
```bash
curl http://localhost:8000/api/health
# {"status": "healthy", "version": "2.0.0", ...}
```

## 📁 Struttura Progetto

```
vinted-optimizer/
├── services/
│   ├── api/                    # FastAPI Backend
│   │   ├── src/
│   │   │   ├── api/v1/         # API endpoints
│   │   │   ├── core/           # Core utilities
│   │   │   ├── db/             # Database models
│   │   │   ├── models/         # SQLAlchemy models
│   │   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── services/       # Business logic
│   │   │   └── main.py         # Entry point
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── fly.toml
│   │
│   ├── frontend/               # Next.js Frontend
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── package.json
│   │
│   ├── ai-service/             # AI Service (locale)
│   │   └── src/
│   │
│   └── scraper-service/        # Scraper Service (locale)
│       └── src/
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🚀 Deploy

### Fly.io (Backend)

```bash
# Installa Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Crea app
fly apps create vinted-optimizer-api

# Configura secrets
fly secrets set DATABASE_URL="postgresql+asyncpg://..."
fly secrets set REDIS_URL="rediss://..."
fly secrets set SECRET_KEY="..."

# Deploy
fly deploy
```

### Neon PostgreSQL

1. Crea account su [neon.tech](https://neon.tech)
2. Crea nuovo progetto
3. Copia `DATABASE_URL` nelle secrets Fly.io

### Upstash Redis

1. Crea account su [upstash.com](https://upstash.com)
2. Crea database Redis
3. Copia `REDIS_URL` nelle secrets Fly.io

## 🧪 Testing

```bash
# Backend tests
cd services/api
uv run pytest --cov=src --cov-report=html

# Con coverage
uv run pytest --cov=src --cov-fail-under=70
```

## 📚 Documentazione

- [`CLAUDE.md`](CLAUDE.md) - Project memory per Kilo Code / GLM-4.7
- [`vinted-enterprise/cove-docs/`](vinted-enterprise/cove-docs/) - Documentazione enterprise completa

## 🔧 Comandi Utili

```bash
# Backend development
uv run fastapi dev src/main.py --port 8000
uv run pytest tests/ -v
uv run ruff check . && uv run ruff format .
uv run mypy src/

# Database migrations
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head

# Docker
docker compose up -d
docker compose logs -f postgres
docker compose down -v
```

## 📊 Stack Tecnologico

| Componente | Tecnologia |
|------------|------------|
| Backend | FastAPI + Python 3.12 |
| Frontend | Next.js 14 + TypeScript |
| Database | Neon PostgreSQL + pgvector |
| Cache | Upstash Redis |
| AI Locale | Ollama + moondream2 |
| Deploy | Fly.io + Cloudflare |
| CI/CD | GitHub Actions |

## 📝 Licenza

MIT License - vedi [LICENSE](LICENSE)

## 👥 Contribuire

1. Fork del repository
2. Crea branch feature (`git checkout -b feature/nuova-funzionalita`)
3. Commit delle modifiche (`git commit -m 'Aggiunta nuova funzionalità'`)
4. Push al branch (`git push origin feature/nuova-funzionalita`)
5. Apri Pull Request
