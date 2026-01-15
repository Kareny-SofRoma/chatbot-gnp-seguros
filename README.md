# 🤖 Chatbot GNP Seguros - Sistema RAG para Agentes

Sistema inteligente de consulta de manuales de seguros GNP usando RAG (Retrieval-Augmented Generation) con Claude 3.5 Sonnet.

## 🎯 Descripción

Chatbot diseñado para **agentes de seguros** que necesitan consultar información de los manuales de GNP de manera rápida y precisa. Utiliza tecnología RAG para buscar en documentos PDF y generar respuestas contextualizadas.

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Frontend       │
│  Next.js 14     │  → Vercel (Deploy)
│  TypeScript     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend        │
│  FastAPI        │  → Railway (Deploy)
│  Python 3.11    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌──────┐ ┌─────────┐
│Pinecone│ │Postgres│ │Redis │ │ Claude  │
│Vectors │ │  DB    │ │Cache │ │ 3.5 API │
└────────┘ └────────┘ └──────┘ └─────────┘
```

## ✨ Características

- 🔍 **Búsqueda Semántica:** Encuentra información relevante en manuales de seguros
- 🧠 **RAG con Claude 3.5 Sonnet:** Respuestas precisas y contextualizadas
- 💾 **Caché Inteligente:** Redis para respuestas rápidas
- 📚 **Multi-Documento:** Soporte para múltiples manuales PDF
- 🔐 **Autenticación:** Sistema de login para agentes
- 📊 **Historial:** Guarda conversaciones y analytics
- 🎨 **UI Moderna:** Interfaz intuitiva con TailwindCSS
- 🚀 **Deploy Fácil:** Vercel + Railway con un click

## 🛠️ Stack Tecnológico

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Lenguaje:** TypeScript
- **Styling:** TailwindCSS + shadcn/ui
- **State:** React Query
- **Deploy:** Vercel

### Backend
- **Framework:** FastAPI
- **Lenguaje:** Python 3.11+
- **RAG:** LangChain
- **LLM Router:** LiteLLM
- **Deploy:** Railway

### Bases de Datos
- **Vectores:** Pinecone (embeddings)
- **Relacional:** PostgreSQL (metadata, usuarios)
- **Caché:** Redis (Upstash)

### IA
- **LLM:** Claude 3.5 Sonnet (Anthropic)
- **Embeddings:** text-embedding-3-small (OpenAI)

## 📦 Estructura del Proyecto

```
chatbot-gnp-seguros/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Configuración
│   │   ├── models/         # Modelos de datos
│   │   └── services/       # Lógica de negocio
│   ├── scripts/            # Scripts de utilidad
│   ├── tests/              # Tests
│   ├── requirements.txt    # Dependencias Python
│   └── Dockerfile
├── frontend/                # Next.js Frontend
│   ├── src/
│   │   ├── app/            # App Router
│   │   ├── components/     # Componentes React
│   │   └── lib/            # Utilidades
│   ├── package.json
│   └── Dockerfile
├── data/
│   └── pdfs/               # 📄 PDFs de manuales GNP
├── docs/                   # Documentación
├── docker-compose.yml      # Desarrollo local
└── README.md
```

## 🚀 Quick Start

### Prerrequisitos

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose (opcional)

### 1. Clonar el repositorio

```bash
git clone https://github.com/Kareny-SofRoma/chatbot-gnp-seguros.git
cd chatbot-gnp-seguros
```

### 2. Configurar variables de entorno

#### Backend (.env en /backend)
```env
# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
PINECONE_API_KEY=pcsk-xxxxx

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/chatbot_gnp
REDIS_URL=redis://localhost:6379

# Pinecone
PINECONE_INDEX_NAME=gnp-seguros
PINECONE_ENVIRONMENT=us-east-1

# App Config
ENVIRONMENT=development
LOG_LEVEL=INFO
```

#### Frontend (.env.local en /frontend)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Instalar dependencias

#### Backend
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### 4. Iniciar con Docker (Recomendado)

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

Servicios disponibles:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 5. O iniciar manualmente

#### Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run dev
```

## 📚 Carga de Manuales PDF

### Agregar PDFs

1. Coloca tus PDFs en `data/pdfs/`
2. Ejecuta el script de procesamiento:

```bash
cd backend
python scripts/process_pdfs.py
```

Este script:
- ✅ Extrae texto de los PDFs
- ✅ Divide en chunks inteligentes
- ✅ Genera embeddings
- ✅ Sube a Pinecone
- ✅ Guarda metadata en PostgreSQL

### Estructura recomendada de PDFs

```
data/pdfs/
├── manual-auto-2024.pdf
├── manual-vida-2024.pdf
├── manual-gastos-medicos.pdf
└── guia-venta-seguros.pdf
```

## 🧪 Testing

### Backend
```bash
cd backend
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm run test
```

## 🚀 Deployment

### Frontend (Vercel)

1. Push a GitHub
2. Conecta tu repo en [Vercel](https://vercel.com)
3. Configura variables de entorno
4. Deploy automático ✅

### Backend (Railway)

1. Conecta tu repo en [Railway](https://railway.app)
2. Selecciona `/backend` como root
3. Configura variables de entorno
4. Deploy automático ✅

Railway incluye:
- ✅ PostgreSQL automático
- ✅ Redis automático
- ✅ SSL/HTTPS
- ✅ Logs y monitoring

## 📊 API Endpoints

### Chat
```
POST /api/v1/chat
Body: {
  "message": "¿Qué cubre el seguro de auto?",
  "conversation_id": "uuid" (opcional)
}
```

### Historial
```
GET /api/v1/conversations/:id
```

### Fuentes
```
GET /api/v1/sources/:query
```

### Upload PDF (Admin)
```
POST /api/v1/admin/upload-pdf
```

Documentación completa: http://localhost:8000/docs

## 🔧 Configuración Avanzada

### Cambiar modelo de LLM

En `backend/app/core/config.py`:
```python
LLM_MODEL = "claude-3-5-sonnet-20241022"  # Default
# LLM_MODEL = "gpt-4o"  # Alternativa
# LLM_MODEL = "gemini-1.5-pro"  # Alternativa
```

### Ajustar parámetros RAG

En `backend/app/services/rag_service.py`:
```python
TOP_K = 5  # Documentos a recuperar
CHUNK_SIZE = 1000  # Tamaño de chunks
CHUNK_OVERLAP = 200  # Overlap entre chunks
```

## 🐛 Troubleshooting

### Error: "Pinecone index not found"
```bash
# Crear índice manualmente
python scripts/create_pinecone_index.py
```

### Error: "Database connection failed"
```bash
# Verificar PostgreSQL
docker-compose ps
docker-compose logs postgres
```

### Error: "Redis connection refused"
```bash
# Verificar Redis
docker-compose ps
docker-compose logs redis
```

## 📈 Roadmap

- [x] Sistema RAG básico
- [x] Interfaz web
- [x] Caché con Redis
- [x] Historial de conversaciones
- [ ] Integración WhatsApp
- [ ] Sistema de feedback
- [ ] Analytics avanzado
- [ ] Multi-idioma
- [ ] Export de conversaciones

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es privado y propiedad de [Tu Empresa].

## 👥 Autores

- **Equipo de Desarrollo** - [Tu Empresa]

## 🙏 Agradecimientos

- GNP Seguros por los manuales
- Anthropic por Claude 3.5 Sonnet
- Pinecone por el vector database
- Railway y Vercel por el hosting

---

**¿Necesitas ayuda?** Abre un issue en GitHub o contacta al equipo de desarrollo.
