# 🚀 Guía de Instalación y Deployment

## 📋 Prerrequisitos

- Docker & Docker Compose instalado
- Node.js 18+ (para desarrollo local sin Docker)
- Python 3.11+ (para desarrollo local sin Docker)
- Git

## 🔧 Instalación Rápida

### 1. Clonar repositorio

```bash
git clone https://github.com/Kareny-SofRoma/chatbot-gnp-seguros.git
cd chatbot-gnp-seguros
```

### 2. Configurar variables de entorno

#### Backend
```bash
cd backend
cp .env.example .env
# Edita .env con tus API keys reales
```

**Variables críticas:**
```env
ANTHROPIC_API_KEY=tu-api-key
OPENAI_API_KEY=tu-api-key
PINECONE_API_KEY=tu-api-key
PINECONE_INDEX_NAME=chatbot-pdfs  # Tu índice existente
```

#### Frontend
```bash
cd ../frontend
cp .env.local.example .env.local
```

### 3. Iniciar con Docker

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

Esto iniciará:
- ✅ PostgreSQL (localhost:5432)
- ✅ Redis (localhost:6379)
- ✅ Backend API (localhost:8000)
- ✅ Frontend (localhost:3000)
- ✅ Adminer (localhost:8080)

### 4. Verificar que todo funcione

```bash
# Health check del backend
curl http://localhost:8000/health

# Abrir frontend
open http://localhost:3000

# Ver API docs
open http://localhost:8000/docs
```

## 🐛 Troubleshooting

### Error: "Port already in use"

```bash
# Ver qué está usando el puerto
lsof -i :8000  # o :3000, :5432, etc

# Matar el proceso
kill -9 <PID>
```

### Error: "Cannot connect to Docker daemon"

```bash
# Iniciar Docker Desktop
open -a Docker

# O iniciar Docker service
sudo systemctl start docker
```

### Error: Frontend no se conecta al backend

Verifica que el .env.local tenga:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Error: "Module not found" en frontend

```bash
cd frontend
rm -rf node_modules .next
npm install
```

## 🔄 Desarrollo sin Docker

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📊 Deployment a Producción

### Frontend (Vercel)

1. Push a GitHub
2. Ir a [vercel.com](https://vercel.com)
3. New Project → Import tu repo
4. Configurar:
   - Framework: Next.js
   - Root Directory: `frontend`
   - Environment Variables:
     ```
     NEXT_PUBLIC_API_URL=https://tu-backend.railway.app
     ```
5. Deploy

### Backend (Railway)

1. Ir a [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Seleccionar tu repo
4. Configurar:
   - Root Directory: `/backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Agregar variables de entorno:
   ```
   ANTHROPIC_API_KEY=...
   OPENAI_API_KEY=...
   PINECONE_API_KEY=...
   PINECONE_INDEX_NAME=chatbot-pdfs
   DATABASE_URL=${DATABASE_URL}  # Railway lo genera
   REDIS_URL=${REDIS_URL}  # Railway lo genera
   ```
6. Agregar PostgreSQL y Redis desde Railway marketplace
7. Deploy

## ✅ Checklist de Deployment

- [ ] Backend desplegado y funcionando
- [ ] PostgreSQL conectado
- [ ] Redis conectado
- [ ] Pinecone conectado (índice existente)
- [ ] Frontend desplegado
- [ ] Frontend se conecta al backend
- [ ] CORS configurado correctamente
- [ ] SSL/HTTPS funcionando
- [ ] Health checks pasando

## 📝 Comandos Útiles

```bash
# Ver logs de Docker
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Detener todo
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Rebuild
docker-compose build --no-cache
docker-compose up -d

# Entrar al contenedor del backend
docker-compose exec backend bash

# Ver base de datos
docker-compose exec postgres psql -U postgres -d chatbot_gnp
```
