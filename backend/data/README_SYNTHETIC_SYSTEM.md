# 🤖 Sistema Automático de Documentos Sintéticos

Sistema completo para procesar PDFs y generar documentos sintéticos consolidados usando IA.

## 📋 Flujo Completo

```
PDFs → Extracción → IA Genera Sintéticos → Sube a Pinecone
```

## 🚀 Uso Rápido

### 1. Coloca tus PDFs
```bash
# Crea el directorio si no existe
mkdir -p backend/data/pdfs_to_process

# Copia tus PDFs ahí
cp /ruta/a/tus/pdfs/*.pdf backend/data/pdfs_to_process/
```

### 2. Extrae texto de PDFs
```bash
cd backend
python scripts/extract_pdfs.py
```

**Qué hace:**
- ✅ Extrae todo el texto de los PDFs
- ✅ Detecta automáticamente el producto (Versátil, Premium, etc.)
- ✅ Identifica secciones (periodos de espera, coberturas, deducibles, etc.)
- ✅ Genera reportes y datos estructurados en `data/extracted/`

### 3. Genera documentos sintéticos con IA
```bash
python scripts/generate_synthetic_docs.py
```

**Qué hace:**
- ✅ Analiza el texto extraído con GPT-4o
- ✅ Consolida información fragmentada
- ✅ Genera documentos sintéticos estructurados
- ✅ Guarda en `data/synthetic/`

### 4. Sube a Pinecone
```bash
python scripts/batch_upload_synthetic.py
```

**Qué hace:**
- ✅ Divide documentos en chunks de 2000 caracteres
- ✅ Genera embeddings
- ✅ Sube vectores a Pinecone con metadatos
- ✅ Marca como `doc_type: synthetic` (prioridad máxima)

## 📁 Estructura de Directorios

```
backend/data/
├── pdfs_to_process/          # ← Coloca tus PDFs aquí
│   ├── manual_versatil.pdf
│   └── manual_premium.pdf
│
├── extracted/                 # Generado por extract_pdfs.py
│   ├── manual_versatil_extracted.txt
│   ├── manual_versatil_report.txt
│   └── manual_versatil_sections.json
│
└── synthetic/                 # Generado por generate_synthetic_docs.py
    ├── synthetic_versatil_periodos_espera.txt
    ├── synthetic_versatil_coberturas.txt
    └── synthetic_premium_deducibles.txt
```

## 🎯 Ventajas del Sistema

### ✅ Automático
- Solo subes PDFs y el sistema hace todo
- No necesitas crear manualmente documentos sintéticos

### ✅ Inteligente
- Detecta productos y categorías automáticamente
- Consolida información fragmentada usando IA
- Elimina duplicados y organiza lógicamente

### ✅ Escalable
- Procesa múltiples PDFs en batch
- Genera múltiples categorías por producto
- Sube todo a Pinecone automáticamente

### ✅ Prioridad en búsquedas
- Los documentos sintéticos tienen `doc_type: synthetic`
- El RAG los prioriza sobre chunks normales
- Respuestas más completas y precisas

## 🔧 Requisitos

```bash
# Instalar PyPDF2 para extracción de PDFs
pip install PyPDF2

# O desde requirements.txt
pip install -r requirements.txt
```

## 📊 Ejemplo Completo

```bash
# 1. Activar entorno virtual
cd backend
source venv/bin/activate

# 2. Copiar PDFs
cp ~/Downloads/manual_*.pdf data/pdfs_to_process/

# 3. Procesar todo
python scripts/extract_pdfs.py
python scripts/generate_synthetic_docs.py
python scripts/batch_upload_synthetic.py

# ¡Listo! Los documentos sintéticos están en Pinecone
```

## 🎨 Personalización

### Agregar nuevos patrones de detección

Edita `extract_pdfs.py` línea ~90:

```python
patterns = {
    'tu_nueva_categoria': [
        r'patrón1',
        r'patrón2'
    ]
}
```

### Cambiar formato de documentos sintéticos

Edita `generate_synthetic_docs.py` línea ~20 (SYNTHETIC_GENERATION_PROMPT)

### Ajustar tamaño de chunks

Edita `batch_upload_synthetic.py` línea ~30:

```python
chunks = chunk_text(content, chunk_size=2000, overlap=200)
```

## 🐛 Troubleshooting

### "No se encontraron PDFs"
→ Verifica que los PDFs estén en `backend/data/pdfs_to_process/`

### "PyPDF2 no está instalado"
→ Ejecuta: `pip install PyPDF2`

### "Error generando embeddings"
→ Verifica que `OPENAI_API_KEY` esté configurada

### "Error subiendo a Pinecone"
→ Verifica que `PINECONE_API_KEY` esté configurada

## 📝 Notas

- Los documentos sintéticos usan chunks grandes (2000 chars) para mantener contexto
- El sistema detecta 8 categorías: periodos_espera, coberturas, deducibles, coaseguros, exclusiones, requisitos, sumas_aseguradas, indemnizaciones
- Puedes ejecutar los scripts múltiples veces, Pinecone actualizará los vectores
- Los documentos sintéticos tienen prioridad en el RAG (ordenados primero)

## 🎯 Resultado

Después de ejecutar el sistema completo:

✅ PDFs procesados y analizados
✅ Documentos sintéticos generados por IA
✅ Vectores subidos a Pinecone con prioridad máxima
✅ Chatbot responde con información completa y consolidada

**¡No más respuestas incompletas por información fragmentada!**
