#!/bin/bash

echo "========================================"
echo "🔍 VERIFICACIÓN PRE-COMMIT"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# 1. Verificar que .env NO está en staging
echo "1️⃣  Verificando archivos .env..."
if git diff --cached --name-only | grep -q ".env$"; then
    echo -e "${RED}❌ ERROR: Archivo .env en staging${NC}"
    echo "   Ejecuta: git reset backend/.env"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}✅ Ningún archivo .env en staging${NC}"
fi
echo ""

# 2. Verificar que existen los archivos .env.example
echo "2️⃣  Verificando archivos .env.example..."
if [ ! -f "backend/.env.example" ]; then
    echo -e "${RED}❌ ERROR: backend/.env.example no existe${NC}"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}✅ backend/.env.example existe${NC}"
fi

if [ ! -f "frontend/.env.local.example" ]; then
    echo -e "${RED}❌ ERROR: frontend/.env.local.example no existe${NC}"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}✅ frontend/.env.local.example existe${NC}"
fi
echo ""

# 3. Verificar que los ejemplos NO tienen API keys reales
echo "3️⃣  Verificando que .env.example NO tiene API keys reales..."
if grep -q "sk-proj-[a-zA-Z0-9]" backend/.env.example 2>/dev/null; then
    if ! grep -q "sk-proj-XXX" backend/.env.example; then
        echo -e "${RED}❌ ERROR: backend/.env.example contiene API key real de OpenAI${NC}"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✅ backend/.env.example usa placeholders${NC}"
    fi
else
    echo -e "${GREEN}✅ backend/.env.example usa placeholders${NC}"
fi
echo ""

# 4. Verificar documentación
echo "4️⃣  Verificando archivos de documentación..."
REQUIRED_DOCS=("README.md" "SETUP.md" "COMMANDS.md" "CONTRIBUTING.md")
for doc in "${REQUIRED_DOCS[@]}"; do
    if [ ! -f "$doc" ]; then
        echo -e "${RED}❌ ERROR: $doc no existe${NC}"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✅ $doc existe${NC}"
    fi
done
echo ""

# 5. Verificar .gitignore
echo "5️⃣  Verificando .gitignore..."
if ! grep -q "^\.env$" .gitignore; then
    echo -e "${RED}❌ ERROR: .gitignore no incluye .env${NC}"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}✅ .gitignore incluye .env${NC}"
fi

if ! grep -q "node_modules" .gitignore; then
    echo -e "${RED}❌ ERROR: .gitignore no incluye node_modules${NC}"
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}✅ .gitignore incluye node_modules${NC}"
fi
echo ""

# 6. Buscar posibles secretos en archivos staged
echo "6️⃣  Buscando posibles secretos en archivos staged..."
STAGED_FILES=$(git diff --cached --name-only)
SECRET_FOUND=0

for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        # Buscar patrones de API keys
        if grep -q "sk-proj-[a-zA-Z0-9]\{20,\}" "$file"; then
            echo -e "${RED}⚠️  ADVERTENCIA: Posible OpenAI API key en $file${NC}"
            SECRET_FOUND=1
        fi
        if grep -q "pcsk_[a-zA-Z0-9-]\{30,\}" "$file"; then
            echo -e "${RED}⚠️  ADVERTENCIA: Posible Pinecone API key en $file${NC}"
            SECRET_FOUND=1
        fi
    fi
done

if [ $SECRET_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No se encontraron secretos en archivos staged${NC}"
fi
echo ""

# Resumen
echo "========================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ TODO LISTO PARA COMMIT${NC}"
    echo ""
    echo "Comando sugerido:"
    echo 'git commit -m "docs: agregar documentación completa del proyecto"'
    echo ""
    exit 0
else
    echo -e "${RED}❌ SE ENCONTRARON $ERRORS ERROR(ES)${NC}"
    echo ""
    echo "Por favor, corrige los errores antes de commitear."
    echo ""
    exit 1
fi
