# VINTED OPTIMIZER — CLAUDE.md (Kilo Code / GLM-4.7)
> **Project Memory** per Kilo Code in VS Code con GLM-4.7 via Z.ai API
> Aggiornato: 2026-02-24 | Versione: 2.0.0

---

## 🎯 PROGETTO

**Vinted Optimizer** è un sistema enterprise per ottimizzare vendite su Vinted.it.
- **Utenti target**: 5-10 account familiari
- **Hardware locale**: iMac 2012 (Intel i5, max 16GB RAM, macOS Catalina)
- **Budget infrastruttura**: €0-15/mese

---

## 🏗️ ARCHITETTURA (SEMPRE RISPETTARE)

```
services/
├── api/           → FastAPI Python 3.12 (Fly.io cloud)
├── frontend/      → Next.js 14 TypeScript (Fly.io / Cloudflare Pages)
├── ai-service/    → FastAPI + Ollama (locale iMac :8001)
├── scraper-service/ → curl-cffi + Playwright (locale iMac :8002)
└── worker/        → ARQ async workers (Fly.io)
```

---

## ⚡ STACK TECNOLOGICO

### Backend (FastAPI)
- Python **3.12+** con **uv** package manager (NON pip, NON conda)
- **FastAPI** + **Pydantic v2** (NON Flask, NON Django)
- **SQLAlchemy 2.0** async + **Alembic** migrations
- **asyncpg** per PostgreSQL, **redis-py** per Upstash Redis
- **ARQ** per background tasks (NON Celery)
- **structlog** per logging (NON logging standard)
- **tenacity** per retry logic
- **httpx** per HTTP client async (NON requests)

### Frontend (Next.js)
- **Next.js 14** App Router + **TypeScript** strict mode
- **Tailwind CSS** + **shadcn/ui** (NON Material-UI, NON Chakra)
- **Zustand** per state (NON Redux)
- **TanStack Query v5** per server state
- **Zod** per validation (NON Yup)
- **Recharts** per grafici
- **Socket.io client** per WebSocket

### AI Service (locale)
- **Ollama** runtime + modelli:
  - `moondream2` → image captioning (1.8GB)
  - `phi3:mini` → text generation (2.3GB)  
  - `nomic-embed-text` → embeddings (0.6GB)
- **curl-cffi** per HTTP con TLS fingerprint (NON requests)
- **DuckDB** per analytics locale (NON SQLite)
- **ChromaDB** per RAG chatbot

### Database
- **Neon PostgreSQL** (serverless branching) con **pgvector**
- **Upstash Redis** (serverless, pay-per-use)
- Schema in `services/api/alembic/versions/`

---

## 📐 CONVENZIONI CODICE

### Python
```python
# ✅ CORRETTO
from pydantic import BaseModel, Field
from typing import Annotated

class ListingCreate(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=255)]
    price: Annotated[float, Field(gt=0, le=9999)]
    
# ❌ SBAGLIATO — non usare dict non tipizzati
def create_listing(data: dict) -> dict: ...
```

```python
# ✅ CORRETTO — async everywhere
async def get_listing(listing_id: UUID, db: AsyncSession) -> Listing:
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    return result.scalar_one_or_none()

# ❌ SBAGLIATO — blocking I/O
def get_listing(listing_id):
    return db.query(Listing).filter(Listing.id == listing_id).first()
```

### TypeScript / React
```tsx
// ✅ CORRETTO — Server Components per default
// app/dashboard/page.tsx
export default async function DashboardPage() {
    const data = await fetchDashboardData()
    return <DashboardView data={data} />
}

// ✅ CORRETTO — Client Components solo quando necessario
"use client"
import { useState } from "react"
```

```tsx
// ✅ CORRETTO — shadcn/ui components
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

// ❌ SBAGLIATO — non usare Material-UI o altri
import { Button } from "@mui/material"
```

### File Naming
```
Python: snake_case.py
TypeScript: kebab-case.ts, PascalCase.tsx per componenti
Test: test_*.py (Python), *.test.ts (TS)
```

---

## 🔑 VARIABILI AMBIENTE

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/vinted
REDIS_URL=rediss://default:xxx@xxx.upstash.io:6380

# Auth
SECRET_KEY=<64-char-random>
ENCRYPTION_KEY=<fernet-key-base64>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Services
AI_SERVICE_URL=http://192.168.1.XXX:8001  # iMac IP
SCRAPER_SERVICE_URL=http://192.168.1.XXX:8002

# Shipping
SENDCLOUD_API_KEY=xxx
SENDCLOUD_API_SECRET=xxx

# Observability
SENTRY_DSN=https://xxx@sentry.io/xxx
OTEL_EXPORTER_OTLP_ENDPOINT=https://xxx.grafana.net:443
OTEL_SERVICE_NAME=vinted-optimizer-api

# Environment
ENV=production
DEBUG=false
LOG_LEVEL=INFO
VERSION=2.0.0
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://api.vinted-optimizer.fly.dev
NEXT_PUBLIC_WS_URL=wss://api.vinted-optimizer.fly.dev
NEXTAUTH_URL=https://vinted-optimizer.fly.dev
NEXTAUTH_SECRET=<32-char-random>
```

---

## 🗂️ COMANDI FREQUENTI

```bash
# Backend
uv run fastapi dev services/api/src/main.py --port 8000
uv run alembic upgrade head
uv run pytest services/api/tests/ -v --cov
uv run ruff check . && uv run ruff format .
uv run mypy services/api/src/

# Frontend
cd services/frontend && npm run dev
npm run build && npm run start
npx biome check --apply .

# AI Service (locale)
cd services/ai-service && uv run fastapi dev src/main.py --port 8001
ollama list
ollama pull moondream2

# Database
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1

# Docker
docker compose up -d postgres redis  # solo dev locale
docker compose logs -f api

# Deploy
fly deploy --app vinted-optimizer-api
fly deploy --app vinted-optimizer-frontend
```

---

## 🧪 TESTING STRATEGY

```python
# Test structure
tests/
├── unit/           # Test funzioni isolate (mocking pesante)
├── integration/    # Test con DB reale (Neon branch test)
├── e2e/            # Playwright tests (solo CI)
└── conftest.py     # Fixtures condivise

# Coverage minimo: 70% per merge
# Run test: pytest -v --cov=src --cov-report=term-missing
```

---

## 🚫 ANTI-PATTERN DA EVITARE

1. **NON** usare `time.sleep()` → usa `asyncio.sleep()`
2. **NON** fare query N+1 → usa `joinedload()` o `selectinload()`
3. **NON** mettere business logic nei router → usa service layer
4. **NON** usare `print()` → usa `structlog`
5. **NON** hardcodare secrets → usa settings da env
6. **NON** scrivere migrazioni SQL a mano → usa Alembic autogenerate
7. **NON** usare `any` in TypeScript → tipa correttamente
8. **NON** mutare state Zustand direttamente → usa immer o set()

---

## 🤖 AI CODING GUIDELINES (per GLM-4.7)

### Quando generi codice:
1. **Sempre** include type hints completi in Python
2. **Sempre** includi error handling con structlog
3. **Sempre** scrivi il corrispondente test unitario
4. **Sempre** usa async/await per I/O
5. **Mai** generare codice sincrono per database o HTTP
6. **Mai** usare librerie non nel pyproject.toml senza chiedermi

### Pattern preferiti:
```python
# Repository pattern per DB access
class ListingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, id: UUID) -> Listing | None:
        ...
    
    async def create(self, data: ListingCreate) -> Listing:
        ...

# Service layer per business logic
class ListingService:
    def __init__(self, repo: ListingRepository, ai: AIService):
        self.repo = repo
        self.ai = ai
    
    async def create_with_ai_analysis(self, data: ListingCreate, image: bytes) -> Listing:
        analysis = await self.ai.analyze_image(image)
        enriched = self._enrich_with_ai(data, analysis)
        return await self.repo.create(enriched)
```

---

## 📦 SERVIZI ESTERNI (Reference)

| Servizio | URL | Piano | Note |
|----------|-----|-------|------|
| Neon PostgreSQL | neon.tech | Free 0.5GB | Branching per dev |
| Upstash Redis | upstash.com | Free 10K req/day | Serverless |
| Fly.io | fly.io | Free $5 credit | Deploy backend |
| Cloudflare Pages | pages.cloudflare.com | Free | Deploy frontend |
| Sendcloud | sendcloud.com | Free 100 ship/mese | Spedizioni |
| 17track | 17track.net/api | Free 100/day | Tracking |
| Sentry | sentry.io | Free 5K errors | Error tracking |
| Grafana Cloud | grafana.com | Free 50GB logs | Monitoring |
| Z.ai API | z.ai | Pay-per-use | GLM fallback |
| Ollama | ollama.ai | Gratis | AI locale |

---

## 🔄 WORKFLOW DI SVILUPPO (Kilo Code)

### Per ogni nuova feature:
1. Crea branch: `feat/nome-feature`
2. Crea/aggiorna schema Pydantic in `schemas/`
3. Crea/aggiorna modello SQLAlchemy in `models/`
4. Crea migrazione Alembic
5. Implementa repository in `repositories/`
6. Implementa service in `services/`
7. Crea router endpoint in `api/v1/`
8. Scrivi test unit + integration
9. Aggiorna documentazione OpenAPI (automatica con FastAPI)
10. PR con CI green → merge

### Istruzioni per task agentico (GSD Mode):
```
Task: Implementa [feature]
Context: Vinted Optimizer Enterprise v2.0
Stack: FastAPI + Next.js 14 + Neon PostgreSQL
Constraints: 
- iMac 2012 per servizi locali (max 8GB RAM disponibile)
- Budget €0-15/mese
- Compatibile con GLM-4.7 Kilo Code workflow

Steps:
1. Leggi CLAUDE.md per contesto
2. Controlla files esistenti correlati
3. Implementa seguendo convenzioni
4. Scrivi test
5. Aggiorna questo CLAUDE.md se hai aggiunto dipendenze
```
