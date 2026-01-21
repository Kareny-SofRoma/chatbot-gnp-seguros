# 🤖 SOIA - Chatbot GNP Seguros

> Sistema RAG inteligente para agentes de seguros con Claude 3.5 Sonnet

<div align="center">

![Status](https://img.shields.io/badge/status-production--ready-success.svg)
![License](https://img.shields.io/badge/license-Private-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)

</div>

---

## 🎯 Descripción

**SOIA** es un chatbot inteligente diseñado para **agentes de seguros** que consultan información de manuales de GNP. Utiliza tecnología RAG (Retrieval-Augmented Generation) con Claude 3.5 Sonnet para respuestas precisas y contextualizadas.

## ✨ Características

- 🔍 **Búsqueda semántica** en manuales PDF
- 🧠 **Claude 3.5 Sonnet** para respuestas naturales
- 💾 **Caché inteligente** con Redis (respuestas <100ms)
- 🛡️ **Rate limiting** para protección contra abuso
- 📊 **Historial de conversaciones** persistente
- 💚 **Health checks** robustos para monitoreo
- 🎨 **UI moderna y minimalista**
- 🚀 **Deploy fácil** con Docker o Railway/Vercel

## 🏗️ Stack Tecnológico

**Frontend:** Next.js 14, TypeScript, TailwindCSS  
**Backend:** FastAPI, Python 3.11, LangChain  
**IA:** Claude 3.5 Sonnet, OpenAI Embeddings  
**Databases:** PostgreSQL, Redis, Pinecone  
**Deploy:** Docker Compose (local), Railway + Vercel (producción)  

## 🚀 Quick Start

### Desarrollo Local

```bash
# 1. Clonar repositorio
git clone https://github.com/Kareny-SofRoma/chatbot-gnp-seguros.git
cd chatbot-gnp-seguros

# 2. Configurar variables de entorno
cd backend && cp .env.example .env
# Edita .env con tus API keys

# 3. Iniciar con Docker Compose
cd .. && docker-compose up -d
```

**Accede a:**
- 🌐 Frontend: http://localhost:3000
- 🔧 API: http://localhost:8000
- 📖 Docs: http://localhost:8000/docs
- 💚 Health: http://localhost:8000/health/detailed

### Deploy a Producción

```bash
# Verificar que todo está listo
python scripts/pre_deploy_check.py

# Seguir guía completa
# Ver: docs/DEPLOY.md
```

**Stack de producción:**
- **Backend:** Railway (PostgreSQL + Redis incluidos)
- **Frontend:** Vercel (CDN global + SSL automático)
- **Vectors:** Pinecone (ya configurado)

**Costo estimado:** $25-65/mes

## 📁 Estructura del Proyecto

```
chatbot-gnp-seguros/
├── backend/              # FastAPI + RAG
│   ├── app/
│   │   ├── api/          # Endpoints REST
│   │   ├── core/         # Config, logging, security
│   │   ├── models/       # SQLAlchemy models
│   │   └── services/     # RAG, LLM, embeddings
│   ├── scripts/          # Procesamiento de PDFs
│   └── Dockerfile        # Producción
├── frontend/             # Next.js
│   └── src/
│       ├── app/          # Pages (App Router)
│       ├── components/   # Componentes React
│       └── lib/          # API client
├── data/pdfs/            # Manuales GNP
├── docs/                 # Documentación
│   ├── DEPLOY.md         # Guía de deploy completa
│   ├── TROUBLESHOOTING.md# Solución de problemas
│   └── INSTALL.md        # Instalación detallada
└── docker-compose.yml    # Desarrollo local
```

## 🔧 Configuración

### Variables de Entorno Críticas

**Backend (.env):**
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
PINECONE_API_KEY=pcsk-xxxxx
PINECONE_INDEX_NAME=chatbot-pdfs
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Ver templates completos:
- `backend/.env.example` (desarrollo)
- `backend/.env.production.example` (producción)

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [INSTALL.md](./docs/INSTALL.md) | Instalación local detallada |
| [DEPLOY.md](./docs/DEPLOY.md) | Deploy a Railway + Vercel |
| [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | Solución de problemas |
| [API Docs](http://localhost:8000/docs) | Documentación interactiva (FastAPI) |

## 🧪 Testing

```bash
# Verificar que todo está listo para deploy
python scripts/pre_deploy_check.py

# Health check completo
curl http://localhost:8000/health/detailed

# Test endpoint de chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué productos de GMM tienen cobertura internacional?"}'
```

## 🚀 Features de Producción

### 🛡️ Seguridad
- ✅ **Rate limiting**: 20 req/min, 100/hora, 500/día
- ✅ **CORS configurado**: Solo dominios autorizados
- ✅ **Validación de env vars**: Falla rápido si falta config
- ✅ **Error handling**: Mensajes user-friendly, no stack traces

### 💚 Monitoreo
- ✅ **Health checks**: `/health`, `/health/detailed`, `/health/ready`, `/health/live`
- ✅ **Logging estructurado**: Railway/Vercel logs integrados
- ✅ **Métricas**: Tokens usados, tiempo de respuesta, cache hits

### ⚡ Performance
- ✅ **Caché inteligente**: Redis con 24h TTL
- ✅ **Query expansion**: Mejora recall en búsquedas
- ✅ **Reranking**: Documentos sintéticos priorizados
- ✅ **Respuestas típicas**: <3 segundos (o <100ms con cache)

## 💰 Costos Estimados

| Servicio | Tier | Costo/mes |
|----------|------|-----------|
| Railway (Backend + DB) | Hobby | $10-20 |
| Vercel (Frontend) | Hobby | $0 |
| Claude API | Pay-as-go | $10-30 |
| OpenAI (Embeddings) | Pay-as-go | $5-15 |
| Pinecone | Free | $0 |
| **Total** | | **$25-65** |

## 🔄 CI/CD

**Auto-deploy configurado:**
- ✅ Push a `main` → Railway redeploy (backend)
- ✅ Push a `main` → Vercel redeploy (frontend)
- ✅ Pull Request → Vercel Preview Deploy

**Workflow:**
```bash
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios ...
git push origin feature/nueva-funcionalidad
# → Vercel crea Preview Deploy automáticamente

# Merge a main
# → Deploy automático a producción
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu branch (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Abre un Pull Request

## 📄 Licencia

Proyecto privado - Todos los derechos reservados

## 🙏 Agradecimientos

- GNP Seguros
- Anthropic (Claude)
- Pinecone
- Railway & Vercel

---

<div align="center">

**¿Preguntas sobre deploy?** Lee [DEPLOY.md](./docs/DEPLOY.md)

**¿Problemas?** Revisa [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)

Made with ❤️ for GNP Insurance Agents

</div>
