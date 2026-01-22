# 📄 Directorio de PDFs de GNP

## Instrucciones

Coloca aquí todos los manuales de GNP en formato PDF que quieres que el chatbot procese.

### Ejemplo de estructura:

```
data/pdfs/
├── manual-auto-gnp-2024.pdf
├── manual-vida-gnp-2024.pdf
├── manual-gastos-medicos-mayores.pdf
├── guia-productos-gnp.pdf
└── etc...
```

### Formatos soportados:
- ✅ PDF con texto seleccionable
- ✅ PDF escaneado (con OCR)
- ✅ Cualquier tamaño de archivo

### Después de agregar PDFs:

1. Ejecuta el script de procesamiento:
```bash
cd backend
python scripts/process_pdfs.py
```

2. El script automáticamente:
   - ✅ Extrae el texto de cada página
   - ✅ Divide el texto en chunks
   - ✅ Genera embeddings
   - ✅ Sube a Pinecone
   - ✅ Guarda metadata en PostgreSQL

### Notas:
- Los PDFs NO se suben al repositorio por seguridad (.gitignore)
- Puedes agregar PDFs en cualquier momento
- Los PDFs ya procesados se omiten automáticamente
