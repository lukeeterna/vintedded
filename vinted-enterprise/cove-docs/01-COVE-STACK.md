# VINTED OPTIMIZER — ENTERPRISE STACK v2.0
> CovE Verified | Ottimizzato per GLM-4.7 Kilo Code su VS Code

---

## 🏗️ ARCHITETTURA MICROSERVIZI

```
vinted-optimizer/
├── services/
│   ├── api/              # FastAPI backend (cloud)
│   ├── frontend/         # Next.js 14 (cloud)
│   ├── ai-service/       # Ollama wrapper (locale iMac)
│   ├── scraper-service/  # curl-cffi + playwright (locale iMac)
│   └── worker/           # Background tasks ARQ (cloud)
├── infra/
│   ├── fly.toml          # Fly.io deployment
│   ├── docker/           # Dockerfiles
│   └── terraform/        # IaC (opzionale)
├── packages/             # Shared packages (monorepo)
│   ├── types/            # Shared TypeScript types
│   └── utils/            # Shared utilities
├── CLAUDE.md             # Kilo Code / Claude Code context
├── .mcp.json             # MCP servers config
└── pyproject.toml        # Python workspace root
```

---

## 🐍 BACKEND — FastAPI Enterprise

### Perché FastAPI > Django per questo progetto (CovE verified)

| Criterio | Django DRF | FastAPI | Winner |
|----------|-----------|---------|--------|
| Performance | ~1000 req/s | ~3000 req/s | FastAPI |
| Async native | No (ASGI addon) | Sì (built-in) | FastAPI |
| OpenAPI auto | Manuale | Automatico | FastAPI |
| Admin panel | Eccellente | Nessuno | Django |
| ORM | Django ORM | SQLAlchemy 2 | Pari |
| Type safety | Parziale | Pydantic v2 nativo | FastAPI |
| Code gen (AI) | Verbose | Conciso | FastAPI |

**Decisione**: FastAPI per API service + SQLAlchemy 2 + Alembic

### Stack Completo Backend

```toml
# pyproject.toml
[project]
name = "vinted-optimizer-api"
requires-python = ">=3.12"
dependencies = [
    # Framework
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "gunicorn>=23.0.0",
    
    # Database
    "sqlalchemy>=2.0.0",
    "alembic>=1.14.0",
    "asyncpg>=0.30.0",          # PostgreSQL async driver
    "redis>=5.2.0",              # Upstash Redis
    
    # Validation & Serialization  
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "msgspec>=0.18.0",           # Ultra-fast serialization
    
    # Auth & Security
    "python-jose[cryptography]>=3.3.0",
    "passlib[argon2]>=1.7.4",
    "python-multipart>=0.0.12",
    
    # HTTP Client
    "httpx>=0.28.0",             # Async HTTP
    "curl-cffi>=0.7.0",          # TLS fingerprinting bypass
    
    # Task Queue
    "arq>=0.26.0",               # Async Redis Queue > Celery
    
    # Observability
    "opentelemetry-sdk>=1.29.0",
    "opentelemetry-instrumentation-fastapi>=0.50b0",
    "sentry-sdk[fastapi]>=2.19.0",
    "structlog>=24.4.0",
    
    # Utils
    "pillow>=11.0.0",
    "python-dotenv>=1.0.0",
    "tenacity>=9.0.0",           # Retry logic
    "anyio>=4.7.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.28.0",            # TestClient
    "factory-boy>=3.3.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
    "pre-commit>=4.0.0",
]
```

### Struttura API Service

```
services/api/
├── src/
│   ├── main.py                 # FastAPI app factory
│   ├── config.py               # Settings con Pydantic
│   ├── database.py             # SQLAlchemy async engine
│   ├── dependencies.py         # FastAPI dependencies
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── router.py       # Include tutti i router
│   │   │   ├── auth.py
│   │   │   ├── listings.py
│   │   │   ├── images.py
│   │   │   ├── sales.py
│   │   │   ├── shipments.py
│   │   │   ├── trends.py
│   │   │   ├── chat.py
│   │   │   └── dashboard.py
│   │   └── health.py
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── listing.py
│   │   ├── sale.py
│   │   ├── shipment.py
│   │   └── trend.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── listing.py
│   │   └── ...
│   │
│   ├── services/               # Business logic layer
│   │   ├── listing_service.py
│   │   ├── ai_service.py       # Proxy to local AI
│   │   ├── shipping_service.py
│   │   └── ...
│   │
│   ├── workers/                # ARQ background tasks
│   │   ├── tasks.py
│   │   └── scheduler.py
│   │
│   └── middleware/
│       ├── cors.py
│       ├── ratelimit.py
│       └── telemetry.py
│
├── tests/
├── alembic/
├── Dockerfile
└── pyproject.toml
```

### main.py Template Enterprise

```python
# services/api/src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import sentry_sdk
import structlog

from .config import settings
from .database import engine
from .api.v1.router import api_v1_router
from .api.health import health_router
from .middleware.ratelimit import RateLimitMiddleware

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle"""
    logger.info("startup", version=settings.VERSION)
    # Verify DB connection
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    logger.info("shutdown")
    await engine.dispose()

def create_app() -> FastAPI:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=settings.ENV,
    )
    
    app = FastAPI(
        title="Vinted Optimizer API",
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)
    
    # Routers
    app.include_router(health_router, prefix="/api")
    app.include_router(api_v1_router, prefix="/api/v1")
    
    # OpenTelemetry
    FastAPIInstrumentor.instrument_app(app)
    
    return app

app = create_app()
```

---

## ⚡ FRONTEND — Next.js 14 Enterprise

### Perché Next.js > React Vite (CovE verified)

| Criterio | React + Vite | Next.js 14 | Winner |
|----------|-------------|-----------|--------|
| SSR/SSG | No | Sì (App Router) | Next.js |
| SEO | No | Sì | Next.js |
| Performance | Buona | Eccellente | Next.js |
| Route-based code split | Manuale | Automatico | Next.js |
| Server Components | No | Sì | Next.js |
| API Routes | No | Sì | Next.js |
| Kilo Code codegen | Standard | Eccellente | Next.js |

### Stack Frontend

```json
{
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "typescript": "^5.7.0",
    
    "tailwindcss": "^3.4.0",
    "@shadcn/ui": "latest",
    "lucide-react": "^0.468.0",
    
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.62.0",
    
    "recharts": "^2.13.0",
    "date-fns": "^4.1.0",
    
    "zod": "^3.23.0",
    "react-hook-form": "^7.54.0",
    "@hookform/resolvers": "^3.9.0",
    
    "socket.io-client": "^4.8.0",
    "next-auth": "^5.0.0",
    
    "@sentry/nextjs": "^8.39.0"
  },
  "devDependencies": {
    "vitest": "^2.1.0",
    "@testing-library/react": "^16.1.0",
    "playwright": "^1.49.0",
    "biome": "^1.9.0"
  }
}
```

**Tailwind + shadcn/ui** > Material-UI perché:
- Zero runtime CSS, bundle più piccolo
- shadcn/ui è copy-paste (no vendor lock-in)
- Kilo Code genera componenti shadcn nativamente
- TypeScript-first, Radix UI primitives

---

## 🤖 AI SERVICE — Ollama Enterprise (locale iMac 2012)

### Stack AI Ottimizzato per iMac 2012

```python
# services/ai-service/src/config.py
# Modelli selezionati per iMac 2012 (max 16GB RAM, no GPU dedicata)

AI_MODELS = {
    # Image captioning: 1.8GB RAM — BEST CHOICE per iMac 2012
    "vision": "moondream2",          
    
    # Text generation per descrizioni listing: 2.3GB RAM
    "text": "phi3:mini",              # Microsoft Phi-3 Mini
    
    # Embeddings per similarità prodotti: 0.6GB RAM
    "embeddings": "nomic-embed-text",
    
    # CLIP per categorizzazione: via Python clip-interrogator
    "clip": "ViT-B-32",              # ~350MB quantizzato INT8
}

# Limiti hardware iMac 2012
MAX_CONCURRENT_REQUESTS = 1
BATCH_SIZE = 1
CACHE_TTL_SECONDS = 3600 * 24  # 24h cache aggressiva
GPU_LAYERS = 0  # CPU only per iMac 2012
```

### Setup Ollama su macOS

```bash
# Install
brew install ollama
brew services start ollama

# Pull modelli ottimizzati
ollama pull moondream2        # 1.8GB - image captioning
ollama pull phi3:mini         # 2.3GB - text generation  
ollama pull nomic-embed-text  # 0.6GB - embeddings

# Test
ollama run phi3:mini "Descrivi questo prodotto Vinted: giacca invernale nera"
```

### AI Service FastAPI

```python
# services/ai-service/src/main.py
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
import httpx
import base64
import sqlite3  # → DuckDB upgrade
from functools import lru_cache
import structlog

logger = structlog.get_logger()
OLLAMA_BASE = "http://localhost:11434"

class ImageAnalysisRequest(BaseModel):
    image_base64: str
    language: str = "it"

class ImageAnalysisResponse(BaseModel):
    category: str
    brand: str | None
    condition: str
    description: str
    suggested_price_range: tuple[float, float]
    tags: list[str]
    confidence: float

async def analyze_image_with_moondream(image_b64: str) -> dict:
    """Usa moondream2 per analisi immagine"""
    prompt = """Analizza questa immagine di un prodotto da vendere su Vinted.
    Rispondi in JSON con: categoria, brand (se visibile), condizione (nuovo/ottimo/buono/usato),
    descrizione (max 200 char), tags (lista parole chiave), prezzo_stimato_min, prezzo_stimato_max."""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": "moondream2",
                "prompt": prompt,
                "images": [image_b64],
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 500}
            }
        )
        return response.json()

app = FastAPI(title="Vinted AI Service", version="2.0.0")

@app.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(req: ImageAnalysisRequest):
    try:
        result = await analyze_image_with_moondream(req.image_base64)
        # Parse JSON from model response
        import json, re
        json_match = re.search(r'\{.*\}', result['response'], re.DOTALL)
        if not json_match:
            raise ValueError("No JSON in response")
        data = json.loads(json_match.group())
        return ImageAnalysisResponse(
            category=data.get("categoria", "altro"),
            brand=data.get("brand"),
            condition=data.get("condizione", "buono"),
            description=data.get("descrizione", ""),
            suggested_price_range=(
                float(data.get("prezzo_stimato_min", 5)),
                float(data.get("prezzo_stimato_max", 50))
            ),
            tags=data.get("tags", []),
            confidence=0.8
        )
    except Exception as e:
        logger.error("ai_analysis_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🕷️ SCRAPER SERVICE — Enterprise Anti-Detection

### Stack Scraping (CovE Upgraded)

```python
# services/scraper-service/requirements.txt
curl-cffi==0.7.2          # TLS fingerprint bypass (SUPERIORE a requests)
playwright==1.49.0         # JS-heavy pages
playwright-stealth==1.0.6  # Anti-detection patches
lxml==5.3.0               # HTML parsing 10x più veloce di BS4
cssselect==1.2.0           # CSS selectors per lxml
aiohttp==3.11.0            # HTTP async pool
apscheduler==4.0.0         # Async scheduler > Celery per task semplici
duckdb==1.1.3              # Analytics locale > SQLite
redis==5.2.0               # Queue e cache
structlog==24.4.0          # Logging strutturato
tenacity==9.0.0            # Retry con backoff
```

### Architettura Scraper Enterprise

```python
# services/scraper-service/src/vinted_scraper.py
import asyncio
import random
from curl_cffi.requests import AsyncSession
from playwright.async_api import async_playwright
import structlog

logger = structlog.get_logger()

# Fingerprint presets per browser realistici
BROWSER_IMPERSONATIONS = [
    "chrome110", "chrome116", "chrome119", 
    "safari15_3", "safari15_5",
    "edge101", "edge110"
]

class VintedScraper:
    """Scraper enterprise con anti-detection avanzato"""
    
    MIN_DELAY = 3.0   # secondi tra richieste
    MAX_DELAY = 8.0
    MAX_RETRIES = 3
    
    def __init__(self):
        self.session = AsyncSession(
            impersonate=random.choice(BROWSER_IMPERSONATIONS),
            verify=False  # per debug; True in prod
        )
    
    async def _request(self, url: str, **kwargs) -> dict:
        """Request con retry e delay randomizzato"""
        from tenacity import retry, stop_after_attempt, wait_random
        
        await asyncio.sleep(random.uniform(self.MIN_DELAY, self.MAX_DELAY))
        
        # Headers realistici
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.vinted.it/",
            "DNT": "1",
        }
        
        response = await self.session.get(
            url, 
            headers={**headers, **kwargs.get("headers", {})},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    async def get_catalog_items(
        self, 
        category_id: int, 
        page: int = 1,
        per_page: int = 96
    ) -> list[dict]:
        """Scrape catalogo pubblico Vinted"""
        url = f"https://www.vinted.it/api/v2/catalog/items"
        params = {
            "page": page,
            "per_page": per_page,
            "catalog_ids[]": category_id,
            "order": "newest_first"
        }
        data = await self._request(url, params=params)
        return data.get("items", [])
    
    async def scrape_trends(self, categories: list[int]) -> list[dict]:
        """Raccoglie dati trend per più categorie"""
        trends = []
        for cat_id in categories:
            try:
                items = await self.get_catalog_items(cat_id, per_page=100)
                trend = self._calculate_trend(cat_id, items)
                trends.append(trend)
                logger.info("trend_scraped", category=cat_id, items=len(items))
            except Exception as e:
                logger.error("trend_scrape_failed", category=cat_id, error=str(e))
        return trends
    
    def _calculate_trend(self, category_id: int, items: list[dict]) -> dict:
        """Calcola statistiche trend da items raw"""
        prices = [float(i.get("price", 0)) for i in items if i.get("price")]
        brands = {}
        for item in items:
            brand = item.get("brand_title", "other")
            brands[brand] = brands.get(brand, 0) + 1
        
        return {
            "category_id": category_id,
            "avg_price": sum(prices) / len(prices) if prices else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "total_items": len(items),
            "top_brands": sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10],
            "sample_items": items[:5]
        }
```

---

## 🚚 SHIPPING SERVICE — Sendcloud Enterprise

### Perché Sendcloud > API Dirette (CovE verified)

| Criterio | API Dirette (Poste/BRT) | Sendcloud API | Winner |
|----------|------------------------|---------------|--------|
| Setup | Contratto commerciale richiesto | Registrazione online | Sendcloud |
| Corrieri | 1 per integrazione | 50+ corrieri | Sendcloud |
| Free tier | No | 100 spedizioni/mese | Sendcloud |
| Etichette | Formato proprietario | PDF standardizzato | Sendcloud |
| Tracking | Solo proprio | Multi-carrier unificato | Sendcloud |

```python
# services/api/src/services/shipping_service.py
import httpx
from pydantic import BaseModel

class ShipmentRequest(BaseModel):
    name: str
    company: str | None = None
    address: str
    city: str
    postal_code: str
    country: str = "IT"
    weight: float  # kg
    description: str
    value: float   # EUR

class SendcloudService:
    BASE_URL = "https://panel.sendcloud.sc/api/v2"
    
    def __init__(self, api_key: str, api_secret: str):
        self.auth = (api_key, api_secret)
    
    async def get_shipping_methods(
        self, 
        from_postal: str, 
        to_postal: str,
        weight: float
    ) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/shipping_methods",
                auth=self.auth,
                params={"from_postal_code": from_postal}
            )
            methods = response.json().get("shipping_methods", [])
            return [m for m in methods if m.get("max_weight", 99) >= weight]
    
    async def create_parcel(self, req: ShipmentRequest, method_id: int) -> dict:
        parcel_data = {
            "parcel": {
                "name": req.name,
                "address": req.address,
                "city": req.city,
                "postal_code": req.postal_code,
                "country": {"iso_2": req.country},
                "weight": str(req.weight),
                "shipment": {"id": method_id},
                "order_number": f"VO-{int(__import__('time').time())}",
                "request_label": True,
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/parcels",
                auth=self.auth,
                json=parcel_data
            )
            return response.json()
```

---

## 💬 CHATBOT — Ollama RAG Enterprise

### Architettura LLM-based (NO Rasa)

```python
# services/api/src/services/chat_service.py
"""
RAG Chatbot con Ollama + ChromaDB
- NO training richiesto
- Zero-maintenance
- Context-aware con dati DB reali
- Streaming responses
"""
import chromadb
import httpx
from fastapi.responses import StreamingResponse
import json

class VintedChatbot:
    SYSTEM_PROMPT = """Sei SARA, assistente AI di Vinted Optimizer.
Hai accesso ai dati reali dell'utente: vendite, listing, spedizioni, trend.
Rispondi in italiano, in modo conciso e utile.
Usa i dati forniti nel contesto per rispondere.
Non inventare dati. Se non sai, dillo chiaramente."""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.chroma = chromadb.Client()
        self.collection = self.chroma.get_or_create_collection("vinted_faq")
    
    async def stream_response(
        self, 
        message: str, 
        user_context: dict,
        history: list[dict]
    ):
        """Stream risposta da Ollama con contesto utente"""
        context = self._build_context(user_context)
        
        messages = [
            {"role": "system", "content": f"{self.SYSTEM_PROMPT}\n\nCONTESTO:\n{context}"},
            *history[-6:],  # ultimi 3 scambi
            {"role": "user", "content": message}
        ]
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.ollama_url}/api/chat",
                json={
                    "model": "phi3:mini",
                    "messages": messages,
                    "stream": True,
                    "options": {"temperature": 0.3}
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if chunk := data.get("message", {}).get("content"):
                            yield f"data: {json.dumps({'text': chunk})}\n\n"
    
    def _build_context(self, ctx: dict) -> str:
        return f"""
Vendite totali: {ctx.get('total_sales', 0)}
Revenue questo mese: €{ctx.get('monthly_revenue', 0):.2f}
Listing attivi: {ctx.get('active_listings', 0)}
Spedizioni pendenti: {ctx.get('pending_shipments', 0)}
Top categoria: {ctx.get('top_category', 'N/A')}
"""
```

---

## 🗄️ DATABASE — Schema Enterprise con pgvector

```sql
-- migrations/001_initial.sql
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector per similarità

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    vinted_username VARCHAR(100),
    vinted_session_encrypted BYTEA,  -- Fernet encrypted
    preferences JSONB DEFAULT '{}',
    role VARCHAR(20) DEFAULT 'member',  -- admin, member
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Listings
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    condition VARCHAR(50),
    size VARCHAR(50),
    colors TEXT[],
    tags TEXT[],
    status VARCHAR(50) DEFAULT 'draft',  -- draft, published, sold, archived
    vinted_id BIGINT UNIQUE,
    vinted_url VARCHAR(500),
    vinted_data JSONB DEFAULT '{}',
    image_embedding vector(512),  -- CLIP embedding per similarità
    ai_analyzed_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Images
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    original_url VARCHAR(500),
    processed_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    storage_path VARCHAR(500),
    metadata JSONB DEFAULT '{}',
    is_primary BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sales
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES listings(id),
    user_id UUID NOT NULL REFERENCES users(id),
    buyer_username VARCHAR(100),
    sale_price DECIMAL(10,2) NOT NULL,
    vinted_fees DECIMAL(10,2) DEFAULT 0,
    net_profit DECIMAL(10,2) GENERATED ALWAYS AS (sale_price - vinted_fees) STORED,
    status VARCHAR(50) DEFAULT 'completed',
    sold_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shipments
CREATE TABLE shipments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_id UUID REFERENCES sales(id),
    carrier VARCHAR(100),
    carrier_service VARCHAR(100),
    tracking_code VARCHAR(100),
    label_url VARCHAR(500),
    shipping_cost DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'pending',
    sendcloud_parcel_id BIGINT,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trends (time-series-like)
CREATE TABLE trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id INTEGER,
    category_name VARCHAR(100),
    avg_price DECIMAL(10,2),
    min_price DECIMAL(10,2),
    max_price DECIMAL(10,2),
    total_items INTEGER,
    top_brands JSONB DEFAULT '[]',
    demand_score INTEGER,
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- user, assistant
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Log
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_listings_user_id ON listings(user_id);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_title_trgm ON listings USING gin(title gin_trgm_ops);
CREATE INDEX idx_listings_embedding ON listings USING ivfflat(image_embedding vector_cosine_ops);
CREATE INDEX idx_sales_user_id ON sales(user_id);
CREATE INDEX idx_sales_sold_at ON sales(sold_at DESC);
CREATE INDEX idx_trends_category ON trends(category_id, scraped_at DESC);
CREATE INDEX idx_audit_user ON audit_log(user_id, created_at DESC);
```

---

## 📊 OSSERVABILITÀ — OpenTelemetry Stack

```python
# services/api/src/middleware/telemetry.py
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
import structlog

def setup_telemetry(app_name: str, otlp_endpoint: str):
    """Setup OpenTelemetry con export a Grafana Cloud"""
    provider = TracerProvider()
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=otlp_endpoint)
        )
    )
    trace.set_tracer_provider(provider)
    
    # Instrumentazioni automatiche
    FastAPIInstrumentor.instrument()
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()
    
    # Logging strutturato con correlation IDs
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
```

---

## 🔐 SECURITY ENTERPRISE

```python
# services/api/src/core/security.py
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import secrets

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class SecurityManager:
    def __init__(self, settings):
        self.settings = settings
        self._fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
    
    def create_access_token(self, user_id: str, role: str) -> str:
        data = {
            "sub": user_id,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "jti": secrets.token_urlsafe(16),  # JWT ID per revoca
        }
        return jwt.encode(data, self.settings.SECRET_KEY, algorithm="HS256")
    
    def encrypt_vinted_session(self, session_data: str) -> bytes:
        """Cripta credenziali Vinted con Fernet AES-128"""
        return self._fernet.encrypt(session_data.encode())
    
    def decrypt_vinted_session(self, encrypted: bytes) -> str:
        return self._fernet.decrypt(encrypted).decode()
```
