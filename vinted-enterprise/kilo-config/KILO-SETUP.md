# KILO CODE SETUP GUIDE — GLM-4.7 via Z.ai
> Guida completa per configurare Kilo Code in VS Code con GLM-4.7
> Target: Sviluppo autonomo Vinted Optimizer Enterprise

---

## 📦 INSTALLAZIONE

### 1. Prerequisiti

```bash
# macOS (iMac 2012 compatibile)
brew install node python@3.12 uv git cloudflared redis ollama

# Node.js 20+ (richiesto per MCP servers)
node --version  # deve essere >= 20

# uv (Python package manager - molto più veloce di pip)
uv --version  # deve essere >= 0.5
```

### 2. Kilo Code in VS Code

```bash
# Installa VS Code se non presente
brew install --cask visual-studio-code

# Installa Kilo Code extension
code --install-extension kilocode.kilo-code

# Oppure: VS Code → Extensions → cerca "Kilo Code"
```

### 3. Z.ai API Key Setup

1. Vai su **z.ai/subscribe**
2. Scegli piano: **GLM Coding Lite** ($3/mese → $6/mese dopo il primo)
3. Dashboard → **API Keys** → copia la key
4. In VS Code: **Kilo Code icon** (sidebar) → **Settings** → **API Provider**
5. Seleziona **Z.ai** dalla lista
6. Incolla API key
7. Seleziona modello: **GLM-4.7** (o glm-4.7-flash per risposte più veloci)

---

## ⚙️ CONFIGURAZIONE MCP SERVERS

### Posizionamento file

```bash
# Project-level MCP (condiviso col team - raccomandate)
cp kilo-config/kilo-mcp-config.json .mcp.json

# User-level MCP (personale - disponibile in tutti i progetti)
cp kilo-config/kilo-mcp-config.json ~/.mcp.json
```

### Variabili d'ambiente (aggiungi a ~/.zshrc o ~/.bash_profile)

```bash
# GitHub
export GITHUB_TOKEN="ghp_your_token_here"

# Database (Neon)
export DATABASE_URL="postgresql+asyncpg://user:pass@ep-xxx.neon.tech/vinted"

# Cache (Upstash)
export REDIS_URL="rediss://default:xxx@xxx.upstash.io:6380"

# Monitoring
export SENTRY_AUTH_TOKEN="sntryu_xxx"

# Deploy
export FLY_API_TOKEN="fo1_xxx"

# Brave Search (opzionale, free)
export BRAVE_API_KEY="BSA_xxx"

# Dev API key
export DEV_API_KEY="dev-secret-key-local"
```

```bash
# Ricarica shell
source ~/.zshrc
```

### Installazione MCP servers Node.js

```bash
# Installa tutti i servers necessari globalmente
npm install -g \
  @modelcontextprotocol/server-filesystem \
  @modelcontextprotocol/server-git \
  @modelcontextprotocol/server-github \
  @modelcontextprotocol/server-postgres \
  @modelcontextprotocol/server-sequential-thinking \
  @modelcontextprotocol/server-fetch \
  @upstash/context7-mcp
```

### Verifica MCP in Kilo Code

```
1. VS Code → Command Palette (Cmd+Shift+P)
2. "Kilo Code: Show MCP Servers"
3. Verifica tutti i server mostrano "connected"
```

---

## 🤖 OLLAMA SETUP (AI Locale)

```bash
# Avvia Ollama (se non già attivo)
brew services start ollama

# Scarica modelli per Vinted Optimizer
# ⚠️ Richiede ~5GB spazio + ~30min per download
ollama pull moondream2        # 1.8GB — image captioning
ollama pull phi3:mini         # 2.3GB — text generation, chatbot
ollama pull nomic-embed-text  # 0.6GB — embeddings

# Verifica
ollama list
# Output atteso:
# NAME                  ID            SIZE    MODIFIED
# moondream2:latest     ...           1.8 GB  ...
# phi3:mini:latest      ...           2.3 GB  ...
# nomic-embed-text:...  ...           0.6 GB  ...

# Test rapido
ollama run phi3:mini "Descrivi una giacca Nike blu in italiano"
```

---

## 🚀 FIRST RUN — Progetto Vinted Optimizer

### Clona e setup

```bash
# Clona repository
git clone https://github.com/yourusername/vinted-optimizer.git
cd vinted-optimizer

# Installa dipendenze Python
uv sync

# Installa dipendenze Node
cd services/frontend && npm install && cd ../..

# Copia .env di sviluppo
cp .env.example .env.development
# Edita .env.development con i tuoi valori
```

### Avvia servizi locali di sviluppo

```bash
# Terminal 1: Backend API
uv run fastapi dev services/api/src/main.py --port 8000

# Terminal 2: Frontend Next.js
cd services/frontend && npm run dev

# Terminal 3: AI Service
cd services/ai-service && uv run fastapi dev src/main.py --port 8001

# Terminal 4: ARQ Worker (background tasks)
uv run arq services.api.src.workers.tasks.WorkerSettings

# Redis locale (dev only)
redis-server &
```

### Verifica tutto funziona

```bash
# API health
curl http://localhost:8000/api/health

# AI Service health
curl http://localhost:8001/health

# Frontend
open http://localhost:3000
```

---

## 💡 TIPS PER PRODUTTIVITÀ MASSIMA CON GLM-4.7

### Prompt Pattern Efficaci

```markdown
# Pattern 1: Feature Implementation
Implementa [FEATURE] in Vinted Optimizer.
Leggi CLAUDE.md per il contesto.
Stack: FastAPI + Next.js 14 + Neon PostgreSQL
Segui i pattern nel CLAUDE.md (Repository + Service layer).
Includi: schema Pydantic, modello SQLAlchemy, migration, service, router, test.

# Pattern 2: Debug
Ho questo errore in [FILE]:
[PASTE ERRORE]
Analizza con Preserved Thinking e fix.
Non cambiare comportamento esterno.
Aggiungi test di regressione.

# Pattern 3: Refactoring
Refactora [FILE/COMPONENT] per:
1. Aggiungere type hints completi
2. Convertire a async/await
3. Aggiungere structlog logging
4. Mantenere stessa API pubblica
Scrivi test prima di refactorare (TDD).

# Pattern 4: Code Review
Review questo codice come senior engineer:
[PASTE CODE]
Identifica: bugs, performance issues, security issues, missing tests.
Suggerisci fix specifici.
```

### Kilo Code Shortcuts

```
Cmd+L         → Apri chat Kilo Code
Cmd+Shift+A   → Add selection to chat
Cmd+I         → Inline edit (modifica file corrente)
@file.py      → Aggiungi file al contesto
@folder/      → Aggiungi cartella al contesto
@CLAUDE.md    → Sempre includere per context
```

### Workflow Ottimale con Preserved Thinking

```markdown
# Prompt con Preserved Thinking abilitato
Voglio implementare [FEATURE COMPLESSA].

Prima pensa al piano (usa <think> blocks):
1. Cosa devo creare/modificare?
2. Quali dipendenze esistenti riuso?
3. Quali test scrivo?
4. Quali edge cases gestisco?

Poi implementa in ordine, verificando dopo ogni step.
```

---

## 🔧 TROUBLESHOOTING

### MCP Server non si connette

```bash
# Debug con log dettagliato
KILO_CODE_DEBUG=1 code .

# Verifica server manualmente
echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | \
  npx @modelcontextprotocol/server-filesystem . 2>/dev/null | head -5
```

### Ollama lento su iMac 2012

```bash
# Verifica RAM disponibile (deve essere >4GB liberi)
vm_stat | grep "Pages free"

# Se RAM insufficiente, chiudi altre app
# Riduci num_predict in chiamate Ollama
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "test",
  "options": {"num_predict": 100, "num_ctx": 1024}
}'
```

### GLM-4.7 risponde lentamente

```markdown
# Usa glm-4.7-flash per task semplici (più veloce, meno costo)
# Usa glm-4.7 con Preserved Thinking per task complessi

# In Kilo Code Settings:
# - Default model: glm-4.7-flash
# - Complex tasks: glm-4.7 (cambio manuale)
```

---

## 📊 COSTI STIMATI Z.AI

| Piano | Prezzo | Incluso | Best For |
|-------|--------|---------|----------|
| Lite | $3/mese | 2.5h/5h window | Uso occasionale |
| Pro | $15/mese | 12.5h/5h window | Sviluppo quotidiano |
| Max | $30/mese | Illimitato | Lavoro intensivo |

**Raccomandazione**: inizia con **Pro ($15/mese)** per sviluppo attivo.
Equivale a ~1/10 del costo di Claude Pro con performance simili.

---

## 🎯 CHECKLIST SETUP COMPLETO

- [ ] VS Code installato
- [ ] Kilo Code extension installata
- [ ] Z.ai account creato + GLM Coding Plan attivato
- [ ] API Key configurata in Kilo Code
- [ ] Node.js 20+ installato
- [ ] uv installato
- [ ] MCP servers Node.js installati globalmente
- [ ] .mcp.json in root progetto
- [ ] Variabili d'ambiente in ~/.zshrc
- [ ] Ollama avviato con modelli scaricati
- [ ] CLAUDE.md in root progetto
- [ ] Backend API avviata in dev mode
- [ ] Frontend avviato in dev mode
- [ ] Test: Kilo Code → chiedi "Leggi CLAUDE.md e dimmi lo stack del progetto"
