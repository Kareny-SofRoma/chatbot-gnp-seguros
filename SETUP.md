# 🚀 GUÍA RÁPIDA DE INSTALACIÓN - 5 MINUTOS

## ✅ Checklist Pre-requisitos

Antes de empezar, verifica que tienes:

- [ ] Docker Desktop instalado y corriendo
- [ ] Node.js 18+ instalado
- [ ] Git instalado
- [ ] OpenAI API Key (pídela al líder del proyecto)
- [ ] Pinecone API Key (pídela al líder del proyecto)

---

## 📥 Paso 1: Clonar el Repositorio (30 segundos)

```bash
git clone <URL_DEL_REPOSITORIO>
cd chatbot
```

---

## ⚙️ Paso 2: Configurar Variables de Entorno (2 minutos)

### **Backend:**

```bash
# 1. Copiar el ejemplo
cp backend/.env.example backend/.env

# 2. Editar con tus API keys
nano backend/.env
# O abre con tu editor favorito: code backend/.env
```

**Reemplaza estas líneas:**
```env
OPENAI_API_KEY=sk-proj-XXXXXXXXXX  ← Pega tu API key real aquí
PINECONE_API_KEY=pcsk_XXXXXXXXXX   ← Pega tu API key real aquí
```

**Guarda el archivo** (Ctrl+X, luego Y, luego Enter en nano)

### **Frontend:**

```bash
# 1. Copiar el ejemplo
cp frontend/.env.local.example frontend/.env.local

# 2. Verificar contenido (no necesita cambios)
cat frontend/.env.local
```

---

## 🐳 Paso 3: Levantar Backend con Docker (1 minuto)

```bash
# Asegúrate de estar en la raíz del proyecto
docker-compose up -d

# Espera 20-30 segundos mientras se inicia todo
```

**Verificar que funciona:**
```bash
# Debe retornar: {"status":"healthy"}
curl http://localhost:8000/health
```

Si ves `{"status":"healthy"}` → ✅ Backend OK

---

## 💻 Paso 4: Instalar y Levantar Frontend (1 minuto)

```bash
cd frontend
npm install
npm run dev
```

**Espera a ver:**
```
✓ Ready in 2.3s
○ Local:   http://localhost:3000
```

---

## 🎉 Paso 5: Probar el Chatbot (30 segundos)

1. Abre tu navegador en: **http://localhost:3000**
2. Escribe: "Hola"
3. Debería responder con el saludo de SOIA
4. Prueba: "Lista todos los seguros de GNP"

Si ves la lista de 69 productos → ✅ **¡TODO FUNCIONA!**

---

## ❌ ¿Algo salió mal?

### **Error: "Connection error"**
```bash
# Verificar que Docker está corriendo
docker-compose ps

# Reiniciar backend
docker-compose restart backend

# Ver logs
docker-compose logs backend --tail=50
```

### **Error: "Port already in use"**
```bash
# Matar proceso en puerto 3000
lsof -ti:3000 | xargs kill -9

# Reintentar
npm run dev
```

### **Error: "API key inválida"**
- Verifica que copiaste correctamente las API keys en `backend/.env`
- No debe haber espacios antes/después de las keys
- Reinicia el backend: `docker-compose restart backend`

---

## 📞 ¿Necesitas Ayuda?

1. Ejecuta el diagnóstico:
   ```bash
   chmod +x diagnose.sh
   ./diagnose.sh
   ```

2. Copia el output completo

3. Contacta al equipo con:
   - El output del diagnóstico
   - Lo que estabas intentando hacer
   - Mensaje de error exacto

---

## 🎯 Siguiente Paso

Lee el **README.md** completo para entender la arquitectura y funcionalidades avanzadas.

---

**¡Listo para desarrollar! 🚀**
