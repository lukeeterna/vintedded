# Setup Infrastruttura Cloud - Vinted Optimizer

Questa guida ti accompagnerà nella configurazione di tutti i servizi cloud necessari per il progetto Vinted Optimizer.

---

## 📋 Prerequisiti

- Account GitHub (✅ già configurato)
- Email per registrare i servizi
- Carta di credito (per verificazione, tutti i servizi hanno piano free)

---

## 1️⃣ Fly.io - Hosting API

### Passi di configurazione:

1. **Vai su** [fly.io/app/sign-up](https://fly.io/app/sign-up)
2. **Registrati** con il tuo account GitHub (più veloce)
3. **Aggiungi una carta di credito** in [fly.io/app/billing](https://fly.io/app/billing)
   - È richiesta per la verifica, ma il piano free include:
   - 3 shared-cpu-1x VMs (256MB RAM)
   - 3GB volume storage
   - 160GB outbound data transfer

4. **Installa Fly CLI** sul tuo Mac:
   ```bash
   brew install flyctl
   ```

5. **Effettua il login**:
   ```bash
   flyctl auth login
   ```

6. **Crea l'applicazione** (dalla cartella `services/api`):
   ```bash
   cd services/api
   flyctl apps create vinted-optimizer-api
   ```

7. **Genera un API token** per GitHub Actions:
   ```bash
   flyctl tokens create deploy -x 999999h
   ```
   Copia il token generato, servirà per GitHub Actions.

### Aggiungi secret a GitHub:
1. Vai su [github.com/lukeeterna/vintedded/settings/secrets/actions](https://github.com/lukeeterna/vintedded/settings/secrets/actions)
2. Clicca "New repository secret"
3. Nome: `FLY_API_TOKEN`
4. Valore: incolla il token generato

---

## 2️⃣ Neon - Database PostgreSQL con pgvector

### Passi di configurazione:

1. **Vai su** [neon.tech](https://neon.tech/)
2. **Clicca "Sign Up"** e registrati con GitHub
3. **Crea un nuovo progetto**:
   - Project name: `vinted-optimizer`
   - Region: `EU (Frankfurt)` - più vicino all'Italia
   - PostgreSQL version: 16 (latest)

4. **Abilita pgvector**:
   - Vai su "SQL Editor" nel dashboard
   - Esegui: `CREATE EXTENSION IF NOT EXISTS vector;`

5. **Copia la stringa di connessione**:
   - Vai su "Connection Details"
   - Copia la "Connection string" (assomiglia a: `postgresql://user:pass@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require`)
   - **Importante**: Cambia `postgresql://` in `postgresql+asyncpg://` per FastAPI

### Salva le credenziali:
Le useremo dopo per configurare `fly secrets`.

---

## 3️⃣ Upstash - Redis

### Passi di configurazione:

1. **Vai su** [upstash.com](https://upstash.com/)
2. **Clicca "Start Free"** e registrati con GitHub
3. **Crea un database Redis**:
   - Name: `vinted-optimizer-redis`
   - Region: `EU (Frankfurt)` o `EU (Ireland)`
   - Type: Regional

4. **Copia la URL di connessione**:
   - Vai su "Details" del database
   - Copia "UPSTASH_REDIS_REST_URL" o la stringa Redis classica
   - Formato: `redis://default:xxx@xxx.upstash.io:6379`

---

## 4️⃣ Configurazione Secrets su Fly.io

Dopo aver ottenuto tutte le credenziali, configura le variabili d'ambiente:

```bash
# Dalla cartella services/api
cd services/api

# Database URL (sostituisci con la tua da Neon)
flyctl secrets set DATABASE_URL="postgresql+asyncpg://user:pass@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require"

# Redis URL (sostituisci con la tua da Upstash)
flyctl secrets set REDIS_URL="redis://default:xxx@xxx.upstash.io:6379"

# Secret key per JWT (genera una nuova)
flyctl secrets set SECRET_KEY="$(openssl rand -hex 32)"

# Encryption key per dati sensibili
flyctl secrets set ENCRYPTION_KEY="$(openssl rand -hex 32)"

# Sentry DSN (opzionale, per monitoring errori)
flyctl secrets set SENTRY_DSN=""
```

---

## 5️⃣ Primo Deploy

Una volta configurati i secrets:

```bash
cd services/api
flyctl deploy
```

Verifica che l'API risponda:
```bash
curl https://vinted-optimizer-api.fly.dev/api/health
```

Dovresti ricevere:
```json
{"status": "healthy", "version": "0.1.0", "environment": "production"}
```

---

## 6️⃣ Monitoring (Opzionale ma Consigliato)

### Better Uptime (Uptime monitoring)
1. Vai su [betteruptime.com](https://betteruptime.com/)
2. Registrati con GitHub
3. Crea un nuovo monitor:
   - URL: `https://vinted-optimizer-api.fly.dev/api/health`
   - Check interval: 5 minuti

### Sentry (Error tracking)
1. Vai su [sentry.io](https://sentry.io/)
2. Registrati (free tier: 5K errori/mese)
3. Crea un progetto Python
4. Copia il DSN e aggiungilo ai fly secrets

---

## ✅ Checklist Finale

- [ ] Fly.io account creato e CLI installata
- [ ] App Fly.io creata: `vinted-optimizer-api`
- [ ] FLY_API_TOKEN aggiunto a GitHub Secrets
- [ ] Neon database creato con pgvector abilitato
- [ ] Upstash Redis creato
- [ ] Tutti i fly secrets configurati
- [ ] Primo deploy completato
- [ ] Health check risponde 200
- [ ] Better Uptime configurato (opzionale)
- [ ] Sentry configurato (opzionale)

---

## 🔗 Link Utili

- [Fly.io Dashboard](https://fly.io/dashboard)
- [Neon Console](https://console.neon.tech/)
- [Upstash Console](https://console.upstash.com/)
- [GitHub Actions](https://github.com/lukeeterna/vintedded/actions)
- [Better Uptime](https://betteruptime.com/)
- [Sentry](https://sentry.io/)

---

## ❓ Problemi Comuni

### "App not found" su Fly.io
Assicurati di essere loggato: `flyctl auth login`

### Database connection failed
Verifica che la stringa di connessione usi `postgresql+asyncpg://` e non `postgresql://`

### Redis connection failed
Verifica che Upstash permetta connessioni dalla regione Fly.io (Frankfurt)

### Deploy fallito
Controlla i log: `flyctl logs`
