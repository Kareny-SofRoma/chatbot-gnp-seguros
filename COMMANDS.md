# 🛠️ COMANDOS ÚTILES PARA DESARROLLO

## 🚀 Comandos de Inicio

```bash
# Levantar TODO el proyecto
docker-compose up -d && cd frontend && npm run dev

# Solo backend
docker-compose up -d

# Solo frontend
cd frontend && npm run dev
```

---

## 📊 Monitoreo y Logs

```bash
# Ver logs en tiempo real del backend
docker-compose logs -f backend

# Ver logs de todos los servicios
docker-compose logs -f

# Ver últimas 50 líneas del backend
docker-compose logs backend --tail=50

# Ver estado de servicios
docker-compose ps
```

---

## 🔄 Reiniciar Servicios

```bash
# Reiniciar backend
docker-compose restart backend

# Reiniciar todo
docker-compose restart

# Detener todo
docker-compose down

# Detener y eliminar volúmenes (⚠️ BORRA LA BASE DE DATOS)
docker-compose down -v
```

---

## 💾 Gestión de Cache

```bash
# Ver estadísticas de Redis (cache)
docker exec chatbot-redis redis-cli INFO stats

# Limpiar TODO el cache
docker exec chatbot-redis redis-cli FLUSHDB

# Ver todas las keys en cache
docker exec chatbot-redis redis-cli KEYS "*"

# Ver cuántas keys hay
docker exec chatbot-redis redis-cli DBSIZE

# Ver valor de una key específica
docker exec chatbot-redis redis-cli GET "pregunta:hola"
```

---

## 🗄️ Base de Datos (PostgreSQL)

```bash
# Conectarse a PostgreSQL
docker exec -it chatbot-postgres psql -U chatbot_user -d chatbot_db

# Dentro de psql:
\dt                          # Listar tablas
\d conversations            # Describir tabla conversations
SELECT COUNT(*) FROM conversations;  # Contar conversaciones
\q                          # Salir
```

**O usar Adminer (interfaz web):**
- URL: http://localhost:8080
- Sistema: PostgreSQL
- Servidor: postgres
- Usuario: chatbot_user
- Contraseña: chatbot_password
- Base de datos: chatbot_db

---

## 🧹 Limpieza y Mantenimiento

```bash
# Limpiar contenedores detenidos
docker system prune

# Limpiar todo (⚠️ PELIGROSO - elimina TODOS los contenedores/imágenes)
docker system prune -a

# Ver uso de disco de Docker
docker system df

# Reconstruir imagen del backend (después de cambios en Dockerfile)
docker-compose build backend
docker-compose up -d backend
```

---

## 🔍 Debugging

```bash
# Entrar al contenedor del backend
docker exec -it chatbot-backend bash

# Ejecutar script de Python dentro del contenedor
docker exec chatbot-backend python scripts/test_query.py

# Ver variables de entorno del backend
docker exec chatbot-backend env | grep OPENAI

# Verificar conectividad a Pinecone
docker exec chatbot-backend python -c "from pinecone import Pinecone; print('OK')"
```

---

## 📦 Frontend

```bash
# Reinstalar dependencias
cd frontend
rm -rf node_modules package-lock.json
npm install

# Limpiar cache de Next.js
rm -rf .next

# Build de producción
npm run build

# Ver problemas de TypeScript
npm run type-check

# Linter
npm run lint
```

---

## 🐛 Troubleshooting Rápido

```bash
# Puerto ocupado
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Reinicio completo
docker-compose down
docker-compose up -d
cd frontend && npm run dev

# Ver IP del contenedor
docker inspect chatbot-backend | grep IPAddress
```

---

## 📊 Diagnóstico Automático

```bash
# Ejecutar script de diagnóstico completo
chmod +x diagnose.sh
./diagnose.sh
```

---

## 🧪 Testing

```bash
# Test de conexión a APIs
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Test de endpoint de chat (requiere jq instalado)
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "conversation_id": null}' | jq

# Test simple sin jq
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "conversation_id": null}'
```

---

## 📝 Git Workflow

```bash
# Estado del repositorio
git status

# Crear nueva rama
git checkout -b feature/nueva-funcionalidad

# Commitear cambios
git add .
git commit -m "feat: descripción del cambio"

# Push a remoto
git push origin feature/nueva-funcionalidad

# IMPORTANTE: Verificar que .env NO está en staging
git status | grep .env
# Si aparece .env, ejecuta:
git reset backend/.env
```

---

## 🔐 Seguridad

```bash
# Verificar que archivos sensibles están en .gitignore
cat .gitignore | grep .env

# Ver qué archivos están trackeados
git ls-files

# Si .env está trackeado por error:
git rm --cached backend/.env
git commit -m "Remove .env from tracking"
```

---

## 💡 Tips de Productividad

```bash
# Alias útiles (agregar a ~/.zshrc o ~/.bashrc)
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcr='docker-compose restart'

# Recargar configuración
source ~/.zshrc  # o ~/.bashrc
```

---

## 🚨 Comandos de Emergencia

```bash
# Si TODO está roto, reinicio completo:
docker-compose down -v
rm -rf frontend/node_modules frontend/.next
docker system prune -f
docker-compose up -d
cd frontend && npm install && npm run dev

# Si cache está causando problemas:
docker exec chatbot-redis redis-cli FLUSHDB
docker-compose restart backend

# Si base de datos está corrupta:
docker-compose down -v
docker-compose up -d
# (Esto borra TODO en la DB, úsalo solo como último recurso)
```

---

**¿Agregaste un comando útil?** Actualiza este archivo para el equipo! 🤝
