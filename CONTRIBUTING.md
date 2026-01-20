# 🤝 GUÍA DE CONTRIBUCIÓN

## 📋 Tabla de Contenidos

- [Código de Conducta](#-código-de-conducta)
- [¿Cómo Contribuir?](#-cómo-contribuir)
- [Convenciones de Código](#-convenciones-de-código)
- [Commits](#-commits)
- [Pull Requests](#-pull-requests)
- [Testing](#-testing)

---

## 🌟 Código de Conducta

- Sé respetuoso con tus compañeros
- Escribe código limpio y documentado
- Pide ayuda cuando la necesites
- Comparte conocimiento con el equipo

---

## 🚀 ¿Cómo Contribuir?

### 1. **Crear una rama**

```bash
# Actualizar main
git checkout main
git pull origin main

# Crear rama de feature
git checkout -b feature/nombre-descriptivo

# O rama de bugfix
git checkout -b fix/nombre-del-bug
```

### 2. **Hacer cambios**

- Escribe código limpio
- Comenta lo complejo
- Prueba tus cambios localmente

### 3. **Commitear**

```bash
git add .
git commit -m "feat: descripción clara del cambio"
```

### 4. **Push y Pull Request**

```bash
git push origin feature/nombre-descriptivo
```

Luego crea un Pull Request en GitHub/GitLab.

---

## 📝 Convenciones de Código

### **Python (Backend)**

```python
# ✅ BIEN: Snake case para variables y funciones
def get_user_data(user_id: str) -> dict:
    user_name = "John Doe"
    return {"name": user_name}

# ❌ MAL: Camel case en Python
def getUserData(userId):
    userName = "John Doe"
    return {"name": userName}

# ✅ BIEN: Docstrings descriptivos
def process_query(query: str) -> str:
    """
    Procesa una consulta del usuario.
    
    Args:
        query: La pregunta del usuario
        
    Returns:
        Respuesta procesada
    """
    return f"Procesando: {query}"

# ✅ BIEN: Type hints
def calculate_score(chunks: List[dict], threshold: float = 0.5) -> int:
    return len([c for c in chunks if c['score'] > threshold])
```

### **TypeScript (Frontend)**

```typescript
// ✅ BIEN: Camel case para variables, Pascal case para componentes
const userName = 'John Doe';

interface UserData {
  name: string;
  email: string;
}

function ChatMessage({ message }: { message: string }) {
  return <div>{message}</div>;
}

// ❌ MAL: Inconsistencia de nombres
const user_name = 'John Doe';  // Snake case en TypeScript
function chat_message() {}      // Snake case para función
```

### **Estructura de Archivos**

```bash
# Backend
app/
  services/
    rag_service.py        # Snake case
    llm_service.py
  models/
    schemas.py

# Frontend
src/
  components/
    ChatMessage.tsx       # Pascal case
    UserProfile.tsx
  lib/
    api.ts               # Camel case
    utils.ts
```

---

## 💬 Commits

### **Formato de Commit Messages**

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
<type>: <description>

[optional body]

[optional footer]
```

### **Tipos de Commits**

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formato, punto y coma faltante, etc (sin cambio de código)
- `refactor:` Refactorización de código
- `test:` Agregar tests
- `chore:` Mantenimiento, actualizar dependencias

### **Ejemplos**

```bash
# ✅ Buenos ejemplos
feat: agregar sistema de cache con Redis
fix: corregir error de conexión a Pinecone
docs: actualizar README con instrucciones de instalación
refactor: optimizar query expansion en RAG
chore: actualizar dependencias de Next.js

# ❌ Malos ejemplos
cambios varios
fix bug
update
WIP
```

---

## 🔀 Pull Requests

### **Antes de crear un PR:**

1. ✅ Prueba localmente
2. ✅ Revisa que no haya console.logs olvidados
3. ✅ Verifica que no subes archivos `.env`
4. ✅ Actualiza documentación si es necesario

### **Título del PR:**

```
feat: Implementar sistema de feedback en respuestas

fix: Corregir formato de respuestas en móvil

docs: Agregar guía de troubleshooting
```

### **Descripción del PR:**

```markdown
## 🎯 Objetivo
Breve descripción del cambio

## 🔧 Cambios
- Cambio 1
- Cambio 2
- Cambio 3

## ✅ Testing
Cómo probaste los cambios

## 📸 Screenshots (si aplica)
[Capturas de pantalla]

## 🔗 Issue relacionado
Closes #123
```

---

## 🧪 Testing

### **Backend**

```bash
# Correr tests (cuando se implementen)
docker exec chatbot-backend pytest

# Test manual de endpoint
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "conversation_id": null}'
```

### **Frontend**

```bash
# TypeScript check
cd frontend
npm run type-check

# Lint
npm run lint

# Build de prueba
npm run build
```

---

## 🚫 Lo que NO debes hacer

- ❌ Commitear archivos `.env`
- ❌ Hacer commits directamente a `main`
- ❌ Dejar `console.log()` en producción
- ❌ Copiar/pegar código sin entenderlo
- ❌ Hacer PRs gigantes (>500 líneas)
- ❌ No documentar funciones complejas

---

## ✅ Buenas Prácticas

- ✅ Commits pequeños y frecuentes
- ✅ Nombre descriptivo para variables
- ✅ Comentarios para lógica compleja
- ✅ Revisar el diff antes de commitear
- ✅ Pedir code review a compañeros
- ✅ Mantener dependencias actualizadas

---

## 📚 Recursos Útiles

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python PEP 8](https://peps.python.org/pep-0008/)
- [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [React Best Practices](https://react.dev/learn)

---

## 🤔 ¿Dudas?

No dudes en preguntar al equipo. Es mejor preguntar que hacer cambios incorrectos.

**Canales de comunicación:**
- Slack: #dev-chatbot
- Reuniones diarias: 10:00 AM
- Code reviews: GitHub/GitLab

---

**¡Gracias por contribuir! 🎉**
