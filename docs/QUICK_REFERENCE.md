# 🚀 Quick Reference - Comandos Útiles

> Referencia rápida de comandos para desarrollo y deployment

---

## 🏠 Desarrollo Local

### Iniciar aplicación

```bash
# Con Docker Compose (recomendado)
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Rebuild después de cambios
docker-compose up -d --build
```

### Sin Docker

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

---

## 🔍 Testing y Validación

### Health Checks

```bash
# Quick check
curl http://localhost:8000/health

# Detailed check (todos los servicios)
curl http://localhost:8000/health/detailed

# Readiness (K8s style)
curl http://localhost:8000/health/ready
```

### Pre-Deploy Check

```bash
# Verificar que todo está listo para deploy
python scripts/pre_deploy_check.py
```

### Validar Variables de Entorno

```bash
# Validar env vars sin iniciar app
python -m app.core.env_validator
```

### Test Chat Endpoint

```bash
# Test query simple
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué productos de GMM tienen cobertura internacional?",
    "user_id": "test_user"
  }'
```

---

## 📊 Database y Redis

### PostgreSQL

```bash
# Conectar a DB local
docker exec -it chatbot-postgres psql -U postgres -d chatbot_gnp

# Ver tablas
\dt

# Ver conversaciones
SELECT * FROM conversations LIMIT 10;

# Ver mensajes
SELECT * FROM messages ORDER BY created_at DESC LIMIT 20;
```

### Redis

```bash
# Conectar a Redis local
docker exec -it chatbot-redis redis-cli

# Ver todas las keys
KEYS *

# Ver cache hits
KEYS rag:v2:*

# Ver rate limit keys
KEYS rate_limit:*

# Limpiar cache
FLUSHDB
```

---

## 🚀 Deploy

### Railway (Backend)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link proyecto
railway link

# Ver logs en tiempo real
railway logs

# Ver variables
railway variables

# Ejecutar comando en Railway
railway run python -m app.core.env_validator
```

### Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy a preview
vercel

# Deploy a production
vercel --prod

# Ver logs
vercel logs
```

---

## 🔧 Mantenimiento

### Procesar nuevos PDFs

```bash
cd backend

# Procesar un PDF específico
python scripts/process_pdfs.py data/pdfs/nuevo_manual.pdf

# Procesar todos los PDFs en directorio
python scripts/process_pdfs.py data/pdfs/

# Ver progreso
tail -f logs/app.log
```

### Limpiar Logs

```bash
# Vaciar logs antiguos
> backend/logs/app.log

# O eliminar completamente
rm backend/logs/*.log
```

### Backup Database

```bash
# Backup PostgreSQL local
docker exec chatbot-postgres pg_dump -U postgres chatbot_gnp > backup.sql

# Restore
docker exec -i chatbot-postgres psql -U postgres chatbot_gnp < backup.sql
```

---

## 🐛 Debug

### Ver logs específicos

```bash
# Errores solamente
docker-compose logs backend | grep ERROR

# Warnings
docker-compose logs backend | grep WARNING

# Performance (tiempos de respuesta)
docker-compose logs backend | grep "⚡"

# Cache hits
docker-compose logs backend | grep "Cache HIT"
```

### Restart servicios individuales

```bash
# Restart backend
docker-compose restart backend

# Restart frontend
docker-compose restart frontend

# Restart PostgreSQL
docker-compose restart postgres

# Restart Redis
docker-compose restart redis
```

### Entrar a container

```bash
# Backend
docker exec -it chatbot-backend bash

# Ver estructura
ls -la app/

# Ver variables de entorno
env | grep -E "(ANTHROPIC|OPENAI|PINECONE)"
```

---

## 📦 Git Workflow

### Feature branch

```bash
# Crear nueva feature
git checkout -b feature/nueva-funcionalidad

# Hacer cambios
git add .
git commit -m "Add: nueva funcionalidad"

# Push
git push origin feature/nueva-funcionalidad

# Crear PR en GitHub
```

### Deploy a producción

```bash
# Asegurarse de estar en main
git checkout main
git pull origin main

# Merge feature
git merge feature/nueva-funcionalidad

# Push (trigger auto-deploy)
git push origin main

# Railway y Vercel deployarán automáticamente
```

### Rollback

```bash
# Ver commits recientes
git log --oneline -10

# Rollback a commit anterior
git reset --hard <commit-hash>

# Force push (¡cuidado!)
git push origin main --force

# Railway/Vercel redeployarán versión anterior
```

---

## 📊 Monitoreo en Producción

### Railway

```bash
# Ver logs
railway logs

# Seguir logs en tiempo real
railway logs --follow

# Ver logs de servicio específico
railway logs --service backend

# Ver métricas
railway status
```

### Verificar deployment

```bash
# Health check producción
curl https://tu-backend.up.railway.app/health/detailed

# Test producción
curl -X POST https://tu-backend.up.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "user_id": "test"}'
```

---

## 🔑 Variables de Entorno

### Listar todas

```bash
# Local (Docker)
docker exec chatbot-backend env

# Railway
railway variables

# Vercel
vercel env ls
```

### Agregar nueva variable

```bash
# Railway
railway variables set NEW_VAR=value

# Vercel
vercel env add NEW_VAR
```

---

## 🧹 Cleanup

### Limpiar Docker

```bash
# Parar y eliminar containers
docker-compose down

# Eliminar volúmenes también
docker-compose down -v

# Limpiar imágenes no usadas
docker image prune -a

# Limpiar todo Docker
docker system prune -a --volumes
```

### Limpiar node_modules

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Limpiar Python cache

```bash
cd backend
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

---

## 💡 Tips Útiles

### Cambiar puerto local

```bash
# Backend
# En docker-compose.yml, cambiar:
ports:
  - "8001:8000"  # Ahora en puerto 8001

# Frontend
# En docker-compose.yml, cambiar:
ports:
  - "3001:3000"  # Ahora en puerto 3001
```

### Ver uso de recursos

```bash
# Docker stats
docker stats

# Específico para app
docker stats chatbot-backend chatbot-frontend
```

### Rate limit test

```bash
# Hacer 25 requests rápidas (debería fallar en #21)
for i in {1..25}; do 
  echo "Request $i"
  curl -X POST http://localhost:8000/api/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"test","user_id":"test"}' \
    -w "\nStatus: %{http_code}\n"
  sleep 0.1
done
```

---

## 🆘 Comandos de Emergencia

### Sistema no responde

```bash
# 1. Ver qué está corriendo
docker ps

# 2. Ver uso de recursos
docker stats

# 3. Restart todo
docker-compose restart

# 4. Si sigue sin funcionar
docker-compose down
docker-compose up -d --build
```

### Base de datos corrupta

```bash
# 1. Backup primero
docker exec chatbot-postgres pg_dump -U postgres chatbot_gnp > emergency_backup.sql

# 2. Eliminar y recrear
docker-compose down -v
docker-compose up -d

# 3. Restore si es necesario
docker exec -i chatbot-postgres psql -U postgres chatbot_gnp < emergency_backup.sql
```

### Cache no funciona

```bash
# Limpiar Redis completamente
docker exec chatbot-redis redis-cli FLUSHALL

# O restart Redis
docker-compose restart redis
```

---

## 📚 Referencias Rápidas

### Endpoints principales

```
GET  /                          # Info básica
GET  /health                    # Quick health
GET  /health/detailed           # Full status
GET  /docs                      # API documentation
POST /api/v1/chat               # Chat endpoint
GET  /api/v1/conversations      # List conversations
```

### Logs importantes

```
⚡ Total time: XXXms            # Tiempo de respuesta
⚡ Cache HIT                    # Cache funcionó
Generated response with XXX tokens  # Uso de Claude
Found XX chunks (best: 0.XXX)  # Calidad de búsqueda
Rate limit exceeded            # Usuario bloqueado
```

### Archivos importantes

```
backend/.env                   # Config local
backend/.env.production.example # Template producción
docker-compose.yml             # Servicios locales
vercel.json                    # Config Vercel
railway.json                   # Config Railway
docs/DEPLOY.md                 # Guía completa deploy
docs/TROUBLESHOOTING.md        # Solución problemas
```

---

**Última actualización:** Enero 2026

**¿Faltan comandos útiles?** Sugiérelos al equipo de desarrollo.
