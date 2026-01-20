#!/bin/bash

echo "======================================"
echo "🔍 DIAGNÓSTICO DEL SISTEMA SOIA"
echo "======================================"
echo ""

# 1. Verificar Docker
echo "1️⃣  Verificando servicios Docker..."
docker-compose ps
echo ""

# 2. Verificar logs del backend
echo "2️⃣  Últimos logs del backend:"
docker-compose logs backend --tail=20
echo ""

# 3. Verificar variables de entorno
echo "3️⃣  Variables de entorno críticas:"
if [ -f backend/.env ]; then
    echo "✅ Archivo .env existe"
    echo "OPENAI_API_KEY: $(grep OPENAI_API_KEY backend/.env | cut -d'=' -f1)=***"
    echo "PINECONE_API_KEY: $(grep PINECONE_API_KEY backend/.env | cut -d'=' -f1)=***"
    echo "PINECONE_INDEX_NAME: $(grep PINECONE_INDEX_NAME backend/.env)"
else
    echo "❌ Archivo .env NO existe"
fi
echo ""

# 4. Test de conectividad
echo "4️⃣  Test de conectividad:"
echo "Backend API:"
curl -s http://localhost:8000/health || echo "❌ Backend no responde"
echo ""

# 5. Verificar Redis
echo "5️⃣  Verificando Redis:"
docker exec chatbot-redis redis-cli PING 2>/dev/null && echo "✅ Redis OK" || echo "❌ Redis no responde"
echo ""

# 6. Verificar PostgreSQL
echo "6️⃣  Verificando PostgreSQL:"
docker exec chatbot-postgres pg_isready 2>/dev/null && echo "✅ PostgreSQL OK" || echo "❌ PostgreSQL no responde"
echo ""

echo "======================================"
echo "✅ Diagnóstico completado"
echo "======================================"
