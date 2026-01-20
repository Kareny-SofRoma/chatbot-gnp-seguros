#!/bin/bash

# 🚀 Script de inicio rápido para SOIA Chatbot

echo "🤖 SOIA - Chatbot GNP Seguros"
echo "================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    echo "Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker no está corriendo"
    echo "Por favor inicia Docker Desktop"
    exit 1
fi

echo "✅ Docker detectado"
echo ""

# Check .env files
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No se encontró backend/.env"
    echo "Copiando desde .env.example..."
    cp backend/.env.example backend/.env
    echo "📝 Por favor edita backend/.env con tus API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - OPENAI_API_KEY"
    echo "   - PINECONE_API_KEY"
    echo ""
    read -p "¿Ya configuraste las API keys? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Por favor configura las API keys y vuelve a ejecutar este script"
        exit 1
    fi
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "⚠️  No se encontró frontend/.env.local"
    echo "Creando archivo por defecto..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
fi

echo "✅ Archivos de configuración listos"
echo ""

# Start services
echo "🐳 Iniciando servicios con Docker Compose..."
echo ""
docker-compose up -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Health check
echo ""
echo "🏥 Verificando salud de los servicios..."
echo ""

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend: http://localhost:8000"
else
    echo "⚠️  Backend no responde aún (puede tardar un poco en iniciar)"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: http://localhost:3000"
else
    echo "⚠️  Frontend no responde aún (puede tardar un poco en iniciar)"
fi

echo "✅ PostgreSQL: localhost:5432"
echo "✅ Redis: localhost:6379"
echo "✅ Adminer: http://localhost:8080"

echo ""
echo "================================"
echo "🎉 ¡SOIA está listo!"
echo ""
echo "📍 Accede a:"
echo "   🌐 Chatbot: http://localhost:3000"
echo "   🔧 API Docs: http://localhost:8000/docs"
echo "   💾 Adminer: http://localhost:8080"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs:     docker-compose logs -f"
echo "   Detener:      docker-compose down"
echo "   Reiniciar:    docker-compose restart"
echo ""
echo "¡Happy chatting! 🚀"
