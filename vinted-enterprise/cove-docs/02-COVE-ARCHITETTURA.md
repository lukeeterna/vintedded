# VINTED OPTIMIZER — ARCHITETTURA ENTERPRISE v2.0
> CovE Revised | Sostituisce architettura-vinted-optimizer.md originale

---

## 🏗️ PANORAMICA SISTEMA

**Vinted Optimizer v2.0** è un sistema enterprise per ottimizzare vendite su Vinted.it con:
- **AI locale** (iMac 2012) per analisi immagini senza costi cloud AI
- **API cloud** (Fly.io) per business logic e storage
- **Frontend cloud** (Cloudflare Pages) per dashboard responsive
- **Tunnel sicuro** (Cloudflare Tunnel) per connettere locale ↔ cloud

---

## 🗺️ ARCHITETTURA COMPLETA

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLOUDFLARE (Edge)                           │
│  ┌─────────────────┐    ┌────────────────────────────────────────┐  │
│  │  Cloudflare CDN  │    │         Cloudflare Pages               │  │
│  │  WAF + DDoS     │───▶│         Next.js 14 Frontend            │  │
│  │  SSL termination│    │         (Static + ISR)                 │  │
│  └────────┬────────┘    └───────────────┬────────────────────────┘  │
└───────────┼──────────────────────────────┼──────────────────────────┘
            │                              │
            ▼                              ▼ API calls
┌─────────────────────────────────────────────────────────────────────┐
│                        FLY.IO Frankfurt                              │
│  ┌─────────────────────────────┐  ┌──────────────────────────────┐  │
│  │     FastAPI API Service     │  │      ARQ Worker               │  │
│  │     Python 3.12             │  │      Background Tasks         │  │
│  │     Pydantic v2             │  │      - Sync vendite Vinted    │  │
│  │     SQLAlchemy 2.0          │  │      - Email notifiche        │  │
│  │     OpenTelemetry           │  │      - Cleanup cache          │  │
│  └──────────────┬──────────────┘  └──────────────────────────────┘  │
└─────────────────┼────────────────────────────────────────────────────┘
                  │
        ┌─────────┼──────────┐
        ▼         ▼          ▼
┌──────────────┐ ┌──────────┐ ┌────────────────────────────────────┐
│    NEON      │ │ UPSTASH  │ │     CLOUDFLARE TUNNEL (Zero Trust) │
│ PostgreSQL   │ │  Redis   │ │     Secure connection to iMac      │
│ + pgvector   │ │Serverless│ │                                    │
│ Serverless   │ │          │ │  ┌────────────────────────────┐    │
└──────────────┘ └──────────┘ │  │     iMac 2012 - Lavello     │   │
                               │  │                             │   │
                               │  │  ┌───────────┐             │   │
                               │  │  │ AI Service│◀── Ollama   │   │
                               │  │  │ :8001     │   moondream │   │
                               │  │  └───────────┘   phi3:mini │   │
                               │  │                             │   │
                               │  │  ┌───────────┐             │   │
                               │  │  │ Scraper   │◀── Redis    │   │
                               │  │  │ Service   │   DuckDB    │   │
                               │  │  │ :8002     │             │   │
                               │  └──┴───────────┘─────────────┘   │
                               └────────────────────────────────────┘
```

---

## 📊 DATABASE SCHEMA v2.0 (con pgvector)

```
USERS (uuid, email, username, password_argon2, vinted_session_fernet,
       preferences jsonb, role, is_active, timestamps)
    │
    ├──◀── LISTINGS (uuid, user_id FK, title, description, price, 
    │               category, brand, condition, size, colors[], tags[],
    │               status, vinted_id, vinted_url, vinted_data jsonb,
    │               image_embedding vector(512), ai_analyzed_at, timestamps)
    │           │
    │           └──◀── IMAGES (uuid, listing_id FK, original_url, 
    │                          processed_url, thumbnail_url, storage_path,
    │                          metadata jsonb, is_primary, display_order)
    │
    ├──◀── SALES (uuid, listing_id FK, user_id FK, buyer_username,
    │             sale_price, vinted_fees, net_profit GENERATED,
    │             status, sold_at, timestamps)
    │           │
    │           └──◀── SHIPMENTS (uuid, sale_id FK, carrier, tracking_code,
    │                             label_url, shipping_cost, status,
    │                             sendcloud_parcel_id, timestamps)
    │
    └──◀── CHAT_SESSIONS (uuid, user_id FK, status, timestamps)
                │
                └──◀── CHAT_MESSAGES (uuid, session_id FK, role, content,
                                      metadata jsonb, created_at)

TRENDS (uuid, category_id, category_name, avg_price, min/max_price,
        total_items, top_brands jsonb, demand_score, scraped_at)

AUDIT_LOG (bigserial, user_id FK, action, resource_type, resource_id,
           ip_address, user_agent, metadata jsonb, created_at)
```

---

## 🔄 FLUSSI PRINCIPALI

### Flusso 1: Upload Immagine → Listing AI-Enhanced

```
Frontend                API                 AI Service          Database
   │                     │                      │                   │
   │──POST /images/──────▶│                      │                   │
   │  multipart/form-data │                      │                   │
   │                     │──resize + optimize───▶│                   │
   │                     │──store → Cloudflare R2│                   │
   │                     │──POST /analyze────────▶│                   │
   │                     │                      │──moondream2────────│
   │                     │                      │──parse JSON        │
   │                     │◀─ analysis result ────│                   │
   │                     │──store embedding──────────────────────────▶│
   │                     │──create listing draft─────────────────────▶│
   │◀─ listing + analysis │                      │                   │
```

### Flusso 2: Vendita → Spedizione → Tracking

```
Frontend        API            Sendcloud        17track        Vinted
   │              │                │               │              │
   │──select sale─▶│                │               │              │
   │              │──get_methods───▶│               │              │
   │◀─ options ───│                │               │              │
   │──confirm ────▶│                │               │              │
   │              │──create_parcel─▶│               │              │
   │              │◀─ label PDF ───│               │              │
   │◀─ label URL ─│                │               │              │
   │              │──ARQ task: ogni 4h polling─────▶│              │
   │              │◀─ status update────────────────│              │
   │              │──WebSocket push a frontend      │              │
```

### Flusso 3: Chatbot RAG

```
Frontend (WebSocket)        API              Chatbot Service      Ollama
        │                    │                     │                 │
        │──message────────────▶│                     │                 │
        │                    │──get user context───▶│                 │
        │                    │──ChromaDB search────▶│                 │
        │                    │──build prompt        │                 │
        │                    │──stream request──────────────────────▶ │
        │◀── stream chunk ───│◀──────────────────── stream──────────  │
        │◀── stream chunk ───│                     │                 │
        │◀── [DONE] ─────────│                     │                 │
```

---

## 🔐 SECURITY ARCHITECTURE

```
┌─────────────────────────────────────────────┐
│              SECURITY LAYERS                │
├─────────────────────────────────────────────┤
│ L1: Cloudflare WAF (DDoS, OWASP rules)     │
│ L2: TLS 1.3 everywhere                     │
│ L3: JWT (HS256, 15min expiry) + Refresh    │
│ L4: Argon2 password hashing                │
│ L5: Fernet AES-128 per Vinted credentials  │
│ L6: Rate limiting (IP + user based)        │
│ L7: CORS strict (allowlist domains)        │
│ L8: Input validation (Pydantic v2)         │
│ L9: SQL injection proof (ORM only)         │
│ L10: Audit log (ogni azione sensibile)     │
│ L11: Secrets in Fly.io vault (never code)  │
│ L12: Cloudflare Tunnel (no port exposure)  │
└─────────────────────────────────────────────┘
```

---

## 📡 API DESIGN v2.0

### Endpoints Completi

```
# Auth
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
DELETE /api/v1/auth/sessions/{jti}   # Revoca token specifico

# Users
GET    /api/v1/users/me
PATCH  /api/v1/users/me
DELETE /api/v1/users/me
POST   /api/v1/users/me/vinted       # Collega Vinted account
GET    /api/v1/users/family          # Lista account familiari (admin)
POST   /api/v1/users/family/invite   # Invita familiare

# Listings
GET    /api/v1/listings              # Paginato, filtri, sort
POST   /api/v1/listings              # Crea (manual o AI-enhanced)
GET    /api/v1/listings/{id}
PATCH  /api/v1/listings/{id}
DELETE /api/v1/listings/{id}
POST   /api/v1/listings/{id}/publish   # → Vinted
POST   /api/v1/listings/{id}/unpublish
POST   /api/v1/listings/{id}/duplicate
GET    /api/v1/listings/similar/{id}   # pgvector similarity search
POST   /api/v1/listings/bulk           # Bulk operations

# Images
POST   /api/v1/images/upload         # Multipart, con AI analysis
GET    /api/v1/images/{id}
DELETE /api/v1/images/{id}
POST   /api/v1/images/{id}/set-primary
POST   /api/v1/images/{id}/reanalyze  # Re-run AI analysis

# Sales
GET    /api/v1/sales                 # Con filtri data, utente
GET    /api/v1/sales/{id}
PATCH  /api/v1/sales/{id}
GET    /api/v1/sales/stats           # KPI aggregati
GET    /api/v1/sales/export          # CSV/Excel download

# Shipments
POST   /api/v1/shipments             # Crea da sale_id
GET    /api/v1/shipments/{id}
GET    /api/v1/shipments/{id}/label  # PDF download
GET    /api/v1/shipments/track/{code}
GET    /api/v1/carriers              # Lista corrieri disponibili
POST   /api/v1/carriers/quote        # Preventivo spedizione

# Trends
GET    /api/v1/trends                # Trend attuali
GET    /api/v1/trends/{category}     # Trend per categoria
GET    /api/v1/trends/brands         # Top brands
POST   /api/v1/trends/refresh        # Trigger scraping (admin)

# Chat
POST   /api/v1/chat/sessions
GET    /api/v1/chat/sessions/{id}
DELETE /api/v1/chat/sessions/{id}
POST   /api/v1/chat/sessions/{id}/messages
GET    /api/v1/chat/sessions/{id}/messages
GET    /api/v1/chat/history

# Dashboard
GET    /api/v1/dashboard/overview
GET    /api/v1/dashboard/analytics   # Dati grafici
GET    /api/v1/dashboard/activity    # Feed attività

# Admin
GET    /api/v1/admin/users           # Tutti gli utenti
GET    /api/v1/admin/metrics         # System metrics
POST   /api/v1/admin/scraper/trigger # Trigger manuale scraper

# Health
GET    /api/health                   # Public health check
GET    /api/health/deep              # Deep check (DB, Redis, AI)
```

---

## 🤖 AI PIPELINE OTTIMIZZATA PER iMac 2012

```
Input: Immagine prodotto (JPEG/PNG, max 10MB)
           │
           ▼
    [Preprocessing - FastAPI]
    - Resize max 1024x1024
    - Normalize JPEG quality 85%
    - Convert to base64
           │
           ▼
    [Cache Check - DuckDB]
    - Hash immagine
    - Se in cache → return cached result
           │ (cache miss)
           ▼
    [moondream2 via Ollama]
    - Prompt ottimizzato in italiano
    - Max 500 tokens output
    - Timeout 60s
    - Temperatura 0.1 (deterministico)
           │
           ▼
    [JSON Extraction + Validation]
    - Regex extract JSON block
    - Pydantic validation
    - Default values se campi mancanti
           │
           ▼
    [Embedding via nomic-embed-text]
    - Embedding del testo descrizione
    - Store in pgvector
           │
           ▼
    Output: {
        "category": "abbigliamento/giacche",
        "brand": "Nike",
        "condition": "ottimo",
        "description": "Giacca sportiva Nike...",
        "suggested_price": {"min": 25.0, "max": 45.0},
        "tags": ["nike", "sportivo", "invernale"],
        "confidence": 0.85
    }
           │
           ▼
    [Cache Store - DuckDB, TTL 24h]
```

---

## 📊 PERFORMANCE TARGETS

| Componente | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| API CRUD | <30ms | <100ms | <300ms |
| API con DB | <50ms | <200ms | <500ms |
| AI Analysis (iMac) | <2s | <5s | <10s |
| Image Upload | <500ms | <2s | <5s |
| Scraper (per item) | 3-8s | 10s | 15s |
| WebSocket message | <50ms | <100ms | <200ms |
| Dashboard load | <200ms | <500ms | <1s |
