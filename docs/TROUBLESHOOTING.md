# 🔧 Troubleshooting Guide

> Soluciones a problemas comunes en producción

---

## 🚨 Problemas Críticos

### ❌ Backend no inicia en Railway

**Síntomas:**
- Build exitoso pero app crashea al iniciar
- Logs muestran: "Application startup failed"

**Posibles causas y soluciones:**

#### 1. Variables de entorno faltantes

```bash
# Logs muestran:
❌ ANTHROPIC_API_KEY is missing

# Solución:
1. Ve a Railway → Backend → Variables
2. Verifica que TODAS las variables críticas estén configuradas
3. Usa el template en backend/.env.production.example
4. Railway re-deployará automáticamente
```

#### 2. Database connection failed

```bash
# Logs muestran:
Error: could not connect to server: Connection refused

# Solución:
1. Verifica que PostgreSQL service esté running
2. Ve a Railway → PostgreSQL → Check status
3. Verifica DATABASE_URL en Backend Variables:
   DATABASE_URL=${{Postgres.DATABASE_URL}}
4. Si sigue fallando, re-create PostgreSQL service
```

#### 3. Redis connection failed

```bash
# Logs muestran:
redis.exceptions.ConnectionError

# Solución:
1. Verifica que Redis service esté running
2. Verifica REDIS_URL en Backend Variables:
   REDIS_URL=${{Redis.REDIS_URL}}
3. Si sigue fallando, restart Redis service
```

---

### ❌ Frontend no puede comunicarse con Backend

**Síntomas:**
- Frontend carga bien pero no obtiene respuestas
- Console error: "Failed to fetch" o "Network error"

**Soluciones:**

#### 1. CORS Error

```bash
# Error en browser console:
Access to fetch at 'https://backend.railway.app/api/v1/chat' 
has been blocked by CORS policy

# Solución:
1. Ve a Railway → Backend → Variables
2. Actualiza ALLOWED_ORIGINS:
   ALLOWED_ORIGINS=https://tu-app.vercel.app
3. NO incluir "/" al final
4. Usa HTTPS, no HTTP
5. Railway re-deployará automáticamente
```

#### 2. URL incorrecta en Frontend

```bash
# Error: 404 Not Found

# Solución:
1. Ve a Vercel → Settings → Environment Variables
2. Verifica NEXT_PUBLIC_API_URL:
   NEXT_PUBLIC_API_URL=https://tu-backend.up.railway.app
3. NO incluir "/" al final
4. Redeploy frontend en Vercel
```

#### 3. Rate Limiting

```bash
# Error: 429 Too Many Requests

# Solución:
1. Esto es normal - rate limit funcionando
2. Espera 1 minuto y vuelve a intentar
3. Si es legítimo, aumenta límites en:
   backend/app/core/rate_limiter.py
4. Push cambios y Railway re-deployará
```

---

## ⚠️ Problemas Comunes

### Build lento en Railway

**Síntoma:** Build tarda más de 5 minutos

**Soluciones:**

1. **Optimizar Dockerfile:**
```dockerfile
# Agregar .dockerignore
__pycache__/
*.pyc
.env
.git/
venv/
logs/
```

2. **Cache de dependencias:**
Railway cachea layers de Docker. Asegúrate de que `COPY requirements.txt` esté antes de `COPY . .`

3. **Usar imagen slim:**
Ya estás usando `python:3.11-slim` ✅

---

### Frontend build falla en Vercel

**Síntoma:** "Build failed" en Vercel

**Posibles causas:**

#### 1. TypeScript errors

```bash
# Error: Type 'string | undefined' is not assignable to type 'string'

# Solución:
1. Fix TypeScript errors localmente:
   cd frontend && npm run build
2. Commit y push fixes
```

#### 2. Environment variable missing

```bash
# Error: process.env.NEXT_PUBLIC_API_URL is undefined

# Solución:
1. Ve a Vercel → Settings → Environment Variables
2. Agrega NEXT_PUBLIC_API_URL
3. Redeploy
```

#### 3. Node version mismatch

```bash
# Error: The engine "node" is incompatible

# Solución:
1. Verifica package.json tenga:
   "engines": {
     "node": ">=18.0.0"
   }
2. O especifica en vercel.json
```

---

### Health check falla en Pinecone

**Síntoma:** `/health/detailed` muestra Pinecone unhealthy

**Soluciones:**

#### 1. API Key inválida

```bash
# Solución:
1. Verifica en Pinecone dashboard que tu API key es válida
2. Actualiza PINECONE_API_KEY en Railway
3. Railway re-deployará
```

#### 2. Index name incorrecto

```bash
# Solución:
1. Ve a Pinecone dashboard
2. Verifica el nombre exacto del índice
3. Actualiza PINECONE_INDEX_NAME en Railway
4. Debe ser exacto: "chatbot-pdfs"
```

#### 3. Region incorrecta

```bash
# Solución:
1. Verifica PINECONE_ENVIRONMENT en Railway
2. Debe coincidir con la region de tu índice
3. Ejemplo: "us-east-1"
```

---

## 🐌 Problemas de Performance

### Respuestas lentas (>10 segundos)

**Diagnóstico:**

1. **Check logs en Railway:**
```bash
# Busca líneas como:
⚡ Total time: 12500ms
```

2. **Identifica el cuello de botella:**
- Si `Total time` es alto pero no hay `Cache HIT` → Pinecone lento
- Si hay errores de Redis → Cache no funciona
- Si tokens_used es muy alto → Contexto muy grande

**Soluciones:**

#### 1. Cache no funcionando

```bash
# Síntoma: Nunca ves "Cache HIT" en logs

# Solución:
1. Verifica Redis en /health/detailed
2. Si Redis falla, restart Redis service en Railway
3. Verifica REDIS_URL en variables
```

#### 2. Pinecone queries lentos

```bash
# Síntoma: Búsqueda tarda >5 segundos

# Solución:
1. Reduce TOP_K en variables de entorno
   TOP_K=3 (en vez de 5)
2. Esto reduce chunks buscados
```

#### 3. LLM response lento

```bash
# Síntoma: Respuesta tarda después de tener contexto

# Solución:
1. Reduce MAX_TOKENS:
   MAX_TOKENS=1500 (en vez de 2000)
2. Reduce contexto enviado a Claude
```

---

### Alto consumo de memoria

**Síntoma:** Railway muestra >500MB memory usage

**Soluciones:**

1. **Limitar workers de Uvicorn:**
```bash
# En Railway variables, agrega:
WEB_CONCURRENCY=2
```

2. **Reducir cache TTL:**
```python
# En rag_service.py:
self.cache_ttl = 43200  # 12 horas en vez de 24
```

3. **Upgrade plan de Railway:**
- Hobby: 512MB RAM
- Pro: 8GB RAM

---

## 💰 Problemas de Costos

### Factura muy alta de Anthropic

**Diagnóstico:**

1. **Check usage en Railway logs:**
```bash
# Busca líneas:
Generated response with 15000 tokens
```

2. **Calcula costo aproximado:**
- Claude 3.5 Sonnet: $3 / million input tokens
- Si tokens_used promedio = 10,000
- 1000 queries = $30

**Soluciones:**

1. **Implementar límites más estrictos:**
```python
# En rate_limiter.py:
requests_per_hour=50  # en vez de 100
```

2. **Reducir contexto enviado:**
```python
# En rag_service.py:
top_chunks = all_chunks[:10]  # en vez de 20
```

3. **Usar modelo más económico:**
```env
# En Railway variables:
LLM_MODEL=claude-3-haiku-20240307
# Haiku es 10x más barato
```

---

### Alto costo de Railway

**Diagnóstico:**

Check usage en Railway Dashboard → Billing

**Soluciones:**

1. **Optimizar database queries:**
- Agregar índices
- Limitar history retrieval

2. **Reducir logs:**
```env
LOG_LEVEL=WARNING  # en vez de INFO
```

3. **Considerar sleep durante low traffic:**
Railway puede hacer sleep de servicios no usados

---

## 📊 Debugging Avanzado

### Ver logs en tiempo real

**Railway:**
```bash
1. Ve a Deployments
2. Click en deployment activo
3. Logs en tiempo real aparecen abajo
```

**Vercel:**
```bash
1. Ve a Deployments
2. Click en deployment
3. Function Logs → Ver logs serverless
```

### Ejecutar comandos en Railway

**Railway CLI:**
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link proyecto
railway link

# Ver logs
railway logs

# Run command
railway run python -m app.core.env_validator
```

### Descargar logs para análisis

```bash
# Railway
railway logs > logs.txt

# Analizar patrones
grep "Error" logs.txt
grep "warning" logs.txt
grep "⚡" logs.txt  # Ver tiempos de respuesta
```

---

## 🆘 Cuando todo lo demás falla

### Rollback a versión anterior

**Railway:**
```bash
1. Ve a Deployments
2. Encuentra último deployment que funcionaba
3. Click "⋮" → "Redeploy"
```

**Vercel:**
```bash
1. Ve a Deployments
2. Encuentra deployment funcional
3. Click "⋮" → "Promote to Production"
```

### Re-crear servicios desde cero

**Railway:**
```bash
1. Exporta todas las variables de entorno
2. Delete servicios problemáticos
3. Crea nuevos servicios
4. Re-configura variables
5. Deploy
```

### Contactar soporte

**Railway:**
- Discord: railway.app/discord
- Email: team@railway.app

**Vercel:**
- Support: vercel.com/support
- Twitter: @vercel

**Anthropic:**
- Support: support.anthropic.com

---

## ✅ Checklist de Debugging

Cuando algo falla, seguir en orden:

- [ ] Check `/health/detailed` endpoint
- [ ] Revisar logs en Railway/Vercel
- [ ] Verificar variables de entorno
- [ ] Test endpoints manualmente con curl
- [ ] Verificar CORS configuration
- [ ] Check rate limiting no está bloqueando
- [ ] Verificar API keys son válidas
- [ ] Test database connection
- [ ] Verificar Pinecone index existe
- [ ] Check que branch correcto está deployed
- [ ] Verificar no hay cambios uncommitted
- [ ] Si todo falla → Rollback

---

**Última actualización:** Enero 2026

**¿No encuentras tu problema?** Busca en:
1. Railway Discord
2. Vercel Community
3. Stack Overflow
4. O pregunta al equipo de desarrollo
