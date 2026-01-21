# 🚀 Guía de Deployment a Producción

> Deploy del Chatbot GNP a Railway (Backend) + Vercel (Frontend)

---

## 📋 **Pre-requisitos**

Antes de empezar, asegúrate de tener:

- ✅ Cuenta en [Railway.app](https://railway.app)
- ✅ Cuenta en [Vercel.com](https://vercel.com)
- ✅ Cuenta en [GitHub](https://github.com)
- ✅ Tu código subido a un repositorio de GitHub
- ✅ API Keys listas:
  - Anthropic API Key
  - OpenAI API Key
  - Pinecone API Key

---

## 🎯 **Arquitectura de Producción**

```
┌─────────────────────────────────────────────┐
│              USUARIOS                       │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│         VERCEL (Frontend)                   │
│  - Next.js App                              │
│  - Auto-deploy desde GitHub                 │
│  - CDN Global                               │
│  - SSL automático                           │
└──────────────┬──────────────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────────────┐
│         RAILWAY (Backend)                   │
│  ┌─────────────────────────────────────┐   │
│  │  FastAPI App                        │   │
│  │  - RAG System                       │   │
│  │  - Claude Integration               │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  PostgreSQL                         │   │
│  │  - Conversaciones                   │   │
│  │  - Mensajes                         │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  Redis                              │   │
│  │  - Caché de respuestas              │   │
│  │  - Rate limiting                    │   │
│  └─────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│         PINECONE (Vectors)                  │
│  - Embeddings de PDFs                       │
│  - Búsqueda semántica                       │
└─────────────────────────────────────────────┘
```

---

# 🛤️ PARTE 1: DEPLOY BACKEND A RAILWAY

## **Paso 1: Preparar el Repositorio**

### 1.1 Asegurar que tu código está en GitHub

```bash
# Si aún no lo has hecho
cd /Users/sofroma01/Documents/chatbot
git add .
git commit -m "Preparando para deploy a producción"
git push origin main
```

### 1.2 Verificar archivos críticos

Asegúrate de que estos archivos existen:

```
chatbot/
├── backend/
│   ├── Dockerfile          ✅
│   ├── requirements.txt    ✅
│   ├── .env.example        ✅
│   └── app/
│       └── main.py         ✅
└── docker-compose.yml      ✅
```

---

## **Paso 2: Crear Proyecto en Railway**

### 2.1 Ir a Railway

1. Ve a [railway.app](https://railway.app)
2. Click en **"Start a New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway a acceder a tu GitHub
5. Selecciona tu repositorio: `chatbot-gnp-seguros`

### 2.2 Configurar Servicios

Railway te preguntará qué desplegar. Necesitas crear **3 servicios**:

#### **Servicio 1: PostgreSQL**

1. Click en **"+ New Service"**
2. Selecciona **"Database"** → **"PostgreSQL"**
3. Railway creará la base de datos automáticamente
4. Anota la variable `DATABASE_URL` (la verás en Variables)

#### **Servicio 2: Redis**

1. Click en **"+ New Service"**
2. Selecciona **"Database"** → **"Redis"**
3. Railway creará Redis automáticamente
4. Anota la variable `REDIS_URL`

#### **Servicio 3: Backend (FastAPI)**

1. Click en **"+ New Service"**
2. Selecciona **"GitHub Repo"**
3. Elige tu repo
4. Railway detectará el Dockerfile automáticamente

---

## **Paso 3: Configurar Variables de Entorno**

### 3.1 En el servicio Backend, ir a **"Variables"**

Click en **"RAW Editor"** y pega esto (reemplazando con tus valores):

```env
# API Keys (REQUERIDO - Usar tus keys reales)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
OPENAI_API_KEY=sk-xxxxx
PINECONE_API_KEY=pcsk_xxxxx

# Database (Railway las proporciona automáticamente)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Pinecone Configuration
PINECONE_INDEX_NAME=chatbot-pdfs
PINECONE_ENVIRONMENT=us-east-1

# App Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=tu-secret-key-super-segura-cambiar-esto

# LLM Configuration
LLM_MODEL=claude-3-5-sonnet-20241022
TEMPERATURE=0.2
MAX_TOKENS=2000

# RAG Configuration
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSION=3072
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5

# CORS (tu dominio de Vercel)
ALLOWED_ORIGINS=https://tu-app.vercel.app,https://chatbot-gnp.vercel.app
```

### 3.2 Railway Reference Variables

Railway usa sintaxis especial para referenciar otros servicios:

- `${{Postgres.DATABASE_URL}}` → URL de tu PostgreSQL
- `${{Redis.REDIS_URL}}` → URL de tu Redis

Railway las reemplazará automáticamente.

---

## **Paso 4: Configurar Dockerfile para Railway**

Railway necesita que el Dockerfile exponga el puerto correcto.

### 4.1 Verificar tu Dockerfile

Asegúrate de que `backend/Dockerfile` tenga:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with Railway's PORT variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Nota:** Railway inyecta la variable `PORT`, así que usamos `${PORT:-8000}`.

---

## **Paso 5: Configurar Railway Settings**

### 5.1 Root Directory

Railway necesita saber dónde está tu backend:

1. Ve a **Settings** del servicio Backend
2. En **"Build"** → **"Root Directory"**
3. Pon: `backend`

### 5.2 Build Command (Opcional)

Railway detectará tu Dockerfile automáticamente, pero si quieres ser explícito:

**Build Command:** (dejar vacío, usará Dockerfile)
**Start Command:** (dejar vacío, usará CMD del Dockerfile)

---

## **Paso 6: Deploy!**

### 6.1 Hacer Deploy

Railway empezará a hacer build automáticamente. Verás:

```
Building...
  → Building Docker image
  → Installing dependencies
  → Starting application
Deployed! ✅
```

### 6.2 Obtener URL pública

1. Ve a **"Settings"** del servicio Backend
2. Click en **"Generate Domain"**
3. Railway te dará una URL como: `chatbot-backend-production.up.railway.app`
4. **Guarda esta URL** - la necesitarás para el frontend

### 6.3 Verificar que funciona

```bash
# Health check
curl https://chatbot-backend-production.up.railway.app/health

# Debería retornar:
{
  "status": "healthy",
  "timestamp": "2026-01-20T..."
}

# Detailed health
curl https://chatbot-backend-production.up.railway.app/health/detailed
```

---

## **Paso 7: Monitoreo en Railway**

### 7.1 Ver Logs

1. Click en el servicio Backend
2. Ve a **"Deployments"**
3. Click en el deployment activo
4. Verás logs en tiempo real

### 7.2 Métricas

Railway te muestra:
- 📊 CPU usage
- 💾 Memory usage
- 🌐 Network traffic
- 💰 Costo estimado

---

# 🌐 PARTE 2: DEPLOY FRONTEND A VERCEL

## **Paso 1: Preparar Frontend**

### 1.1 Crear archivo de configuración de Vercel

Crea `vercel.json` en la raíz del proyecto:

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

### 1.2 Verificar package.json

Tu `frontend/package.json` debe tener:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

---

## **Paso 2: Deploy a Vercel**

### 2.1 Conectar Repositorio

1. Ve a [vercel.com](https://vercel.com)
2. Click en **"Add New Project"**
3. Importa tu repositorio de GitHub
4. Vercel detectará Next.js automáticamente

### 2.2 Configurar Root Directory

En la configuración de Vercel:

- **Root Directory:** `frontend`
- **Framework Preset:** Next.js
- **Build Command:** `npm run build` (auto-detectado)
- **Output Directory:** `.next` (auto-detectado)

---

## **Paso 3: Variables de Entorno en Vercel**

### 3.1 Agregar Environment Variables

En Vercel → **Settings** → **Environment Variables**:

```env
NEXT_PUBLIC_API_URL=https://chatbot-backend-production.up.railway.app
```

**⚠️ IMPORTANTE:** 
- Usa la URL de Railway (sin `/` al final)
- Debe empezar con `NEXT_PUBLIC_` para estar disponible en el browser

### 3.2 Variables por entorno (Opcional)

Puedes tener diferentes URLs para:
- **Production:** Tu Railway URL
- **Preview:** Railway URL de staging
- **Development:** `http://localhost:8000`

---

## **Paso 4: Deploy!**

### 4.1 Hacer Deploy

1. Click en **"Deploy"**
2. Vercel hará build y deploy automáticamente
3. Verás el progreso en tiempo real

### 4.2 Obtener URL

Vercel te dará una URL como:
- `chatbot-gnp-xxxx.vercel.app` (auto-generada)
- O puedes usar tu dominio custom

---

## **Paso 5: Configurar Dominio Custom (Opcional)**

### 5.1 Si tienes dominio propio

1. Ve a **Settings** → **Domains**
2. Agrega tu dominio: `chatbot.tuempresa.com`
3. Vercel te dará registros DNS a configurar:

```
Type: CNAME
Name: chatbot
Value: cname.vercel-dns.com
```

4. Agrega estos registros en tu proveedor DNS (GoDaddy, Namecheap, etc.)
5. Espera 1-24 horas para propagación
6. ✅ SSL automático con Let's Encrypt

---

## **Paso 6: Actualizar CORS en Backend**

Ahora que tienes la URL de Vercel, actualiza el backend:

### 6.1 En Railway → Backend → Variables

Actualiza `ALLOWED_ORIGINS`:

```env
ALLOWED_ORIGINS=https://chatbot-gnp-xxxx.vercel.app,https://chatbot.tuempresa.com
```

### 6.2 Redeploy Backend

Railway re-deployará automáticamente al cambiar variables.

---

## **Paso 7: Verificar que Todo Funciona**

### 7.1 Test End-to-End

1. Abre tu URL de Vercel: `https://chatbot-gnp-xxxx.vercel.app`
2. Escribe una pregunta en el chat
3. Deberías ver la respuesta del backend

### 7.2 Si algo falla

**Check 1: CORS Error**
```
Access to fetch at '...' has been blocked by CORS policy
```
→ Verifica `ALLOWED_ORIGINS` en Railway

**Check 2: 404 Not Found**
```
Failed to fetch
```
→ Verifica que `NEXT_PUBLIC_API_URL` sea correcta

**Check 3: 500 Internal Error**
→ Revisa logs en Railway → Backend → Deployments

---

# 🔄 CI/CD - Auto-Deploy

## **Auto-Deploy Configurado ✅**

Ambos servicios ya tienen auto-deploy:

### Railway (Backend)
- **Trigger:** Push a `main` branch
- **Build:** Automático
- **Deploy:** Automático

### Vercel (Frontend)
- **Trigger:** Push a `main` branch
- **Build:** Automático
- **Deploy:** Automático
- **Preview:** Automático en Pull Requests

### Workflow

```bash
# 1. Hacer cambios localmente
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios ...

# 2. Commit y push
git add .
git commit -m "Agregar nueva funcionalidad"
git push origin feature/nueva-funcionalidad

# 3. Crear Pull Request en GitHub
# → Vercel creará un Preview Deploy automáticamente

# 4. Merge a main
# → Vercel deploy a producción
# → Railway deploy a producción

# ✅ Todo automático
```

---

# 💰 Costos Estimados

## Railway (Backend)

**Plan Hobby (Recomendado para empezar):**
- $5/mes + uso
- Incluye: 500 horas de ejecución, $5 de crédito
- PostgreSQL + Redis incluidos
- **Costo real estimado:** $10-20/mes

**Plan Pro:**
- $20/mes + uso
- Sin límites de horas
- **Costo real estimado:** $30-50/mes

## Vercel (Frontend)

**Plan Hobby (Free):**
- ✅ 100 GB bandwidth/mes
- ✅ Deployments ilimitados
- ✅ Dominios custom
- ✅ SSL automático
- **Costo:** $0/mes

**Plan Pro:**
- $20/mes
- 1 TB bandwidth
- **Solo si necesitas más tráfico**

## APIs Externas

- **Anthropic (Claude):** ~$10-30/mes (depende de uso)
- **OpenAI (Embeddings):** ~$5-15/mes
- **Pinecone:** $0 (Free tier) o $70/mes (Standard)

## **Total Estimado: $25-65/mes**

Para una startup, esto es muy razonable.

---

# 🐛 Troubleshooting

## Error: "Database connection failed"

**Síntoma:** Health check falla en PostgreSQL

**Solución:**
```bash
# 1. Verifica que DATABASE_URL esté configurada
# 2. En Railway, ve a PostgreSQL → Connect
# 3. Copia la nueva DATABASE_URL
# 4. Actualiza en Backend Variables
```

## Error: "Redis connection failed"

**Síntoma:** Health check falla en Redis

**Solución:**
```bash
# 1. Verifica REDIS_URL
# 2. En Railway, verifica que Redis esté running
# 3. Restart el servicio Redis si es necesario
```

## Error: "Pinecone index not found"

**Síntoma:** Health check falla en Pinecone

**Solución:**
```bash
# 1. Verifica PINECONE_API_KEY
# 2. Verifica PINECONE_INDEX_NAME (debe ser exacto)
# 3. Ve a Pinecone dashboard y confirma que el índice existe
```

## Error: "Build failed"

**Síntoma:** Railway no puede hacer build

**Solución:**
```bash
# 1. Verifica que requirements.txt esté completo
# 2. Verifica que Dockerfile esté correcto
# 3. Revisa los logs de build en Railway
# 4. Verifica Root Directory = "backend"
```

## Error: CORS en producción

**Síntoma:** Frontend no puede hacer requests

**Solución:**
```bash
# 1. Verifica ALLOWED_ORIGINS incluye tu dominio de Vercel
# 2. NO incluir "/" al final
# 3. Usa HTTPS, no HTTP
# Ejemplo correcto:
ALLOWED_ORIGINS=https://tu-app.vercel.app
```

## Error: "Environment variable missing"

**Síntoma:** App falla al iniciar

**Solución:**
```bash
# El env_validator te dirá exactamente qué falta
# Agrega la variable en Railway → Variables
# Railway re-deployará automáticamente
```

---

# ✅ Checklist Final

## Antes de Deploy

- [ ] Código pushed a GitHub
- [ ] `.env.example` actualizado
- [ ] Dockerfile correcto
- [ ] API Keys listas

## Deploy Backend (Railway)

- [ ] PostgreSQL creado
- [ ] Redis creado
- [ ] Backend service creado
- [ ] Variables de entorno configuradas
- [ ] Root directory = "backend"
- [ ] Domain generado
- [ ] Health check pasa: `/health/detailed`

## Deploy Frontend (Vercel)

- [ ] Proyecto importado
- [ ] Root directory = "frontend"
- [ ] `NEXT_PUBLIC_API_URL` configurada
- [ ] Deploy exitoso
- [ ] App funciona en browser

## Post-Deploy

- [ ] CORS configurado en backend
- [ ] Test end-to-end funciona
- [ ] Dominio custom (opcional)
- [ ] Monitoreo configurado
- [ ] Logs accesibles

---

# 🎉 ¡Listo para Producción!

Tu chatbot ahora está:

✅ **Desplegado** en infraestructura profesional
✅ **Escalable** con Railway y Vercel  
✅ **Seguro** con rate limiting y validación  
✅ **Monitoreable** con health checks  
✅ **Auto-deployable** con CI/CD  

**URLs de tu app:**
- Frontend: `https://tu-app.vercel.app`
- Backend API: `https://tu-backend.up.railway.app`
- Docs: `https://tu-backend.up.railway.app/docs`
- Health: `https://tu-backend.up.railway.app/health/detailed`

---

**¿Preguntas?** Revisa la sección de Troubleshooting o contacta al equipo de desarrollo.

**Última actualización:** Enero 2026
