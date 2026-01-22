"""
Generador automático de documentos sintéticos usando IA

Este script usa GPT-4o para analizar el texto extraído y generar
documentos sintéticos consolidados de alta calidad.

Uso:
    python backend/scripts/generate_synthetic_docs.py
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.llm_service import llm_service
from app.core.logger import get_logger

logger = get_logger()

SYNTHETIC_GENERATION_PROMPT = """Eres un experto en consolidar información fragmentada de manuales de seguros.

Tu tarea es crear un DOCUMENTO SINTÉTICO que consolide TODA la información sobre un tema específico que está fragmentada en múltiples páginas.

CONTEXTO EXTRAÍDO:
{context}

PRODUCTO: {product}
CATEGORÍA: {category}

INSTRUCCIONES:

1. ANALIZA toda la información proporcionada
2. CONSOLIDA la información eliminando duplicados
3. ORGANIZA por categorías lógicas
4. USA el siguiente formato EXACTO:

═══════════════════════════════════════════════════════════════
{category_title} - PRODUCTO {product_upper}
═══════════════════════════════════════════════════════════════

DOCUMENTO SINTÉTICO CONSOLIDADO

[Breve descripción del contenido]

═══════════════════════════════════════════════════════════════

[SECCIÓN 1]:

[Contenido organizado con viñetas o subsecciones]

═══════════════════════════════════════════════════════════════

[SECCIÓN 2]:

[Contenido organizado con viñetas o subsecciones]

═══════════════════════════════════════════════════════════════

CONSIDERACIONES IMPORTANTES:

[Lista de notas importantes, excepciones, etc.]

═══════════════════════════════════════════════════════════════

PRODUCTO: {product}
TIPO: [Tipo de seguro]
CATEGORÍA: {category}
DOCUMENTO: Síntesis completa

REGLAS CRÍTICAS:
- NO inventes información
- SOLO usa lo que está en el contexto
- Si falta información, NO la incluyas
- Mantén números, montos y plazos EXACTOS
- Usa formato profesional y claro
- Incluye TODA la información relevante encontrada

Genera SOLO el documento sintético, sin explicaciones adicionales."""

def load_extracted_data(extracted_dir: Path):
    """Carga datos extraídos de PDFs"""
    sections_files = list(extracted_dir.glob("*_sections.json"))
    
    if not sections_files:
        print(f"❌ No se encontraron archivos *_sections.json en: {extracted_dir}")
        return []
    
    all_data = []
    
    for sections_file in sections_files:
        with open(sections_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Cargar texto completo
            text_file = sections_file.parent / f"{sections_file.stem.replace('_sections', '_extracted')}.txt"
            if text_file.exists():
                with open(text_file, 'r', encoding='utf-8') as tf:
                    data['full_text'] = tf.read()
            
            all_data.append({
                'filename': sections_file.stem,
                'data': data
            })
    
    return all_data

def generate_synthetic_doc(product: str, category: str, context: str) -> str:
    """Genera documento sintético usando IA"""
    
    category_titles = {
        'periodos_espera': 'PERIODOS DE ESPERA',
        'coberturas': 'COBERTURAS Y BENEFICIOS',
        'deducibles': 'DEDUCIBLES',
        'coaseguros': 'COASEGUROS',
        'exclusiones': 'EXCLUSIONES Y LIMITACIONES',
        'requisitos': 'REQUISITOS Y DOCUMENTACIÓN',
        'sumas_aseguradas': 'SUMAS ASEGURADAS Y LÍMITES',
        'indemnizaciones': 'INDEMNIZACIONES Y PAGOS'
    }
    
    category_title = category_titles.get(category, category.upper().replace('_', ' '))
    product_upper = product.upper()
    
    prompt = SYNTHETIC_GENERATION_PROMPT.format(
        context=context[:15000],  # Límite de contexto
        product=product,
        category=category,
        category_title=category_title,
        product_upper=product_upper
    )
    
    print(f"\n🤖 Generando documento sintético con IA...")
    print(f"   📦 Producto: {product}")
    print(f"   🏷️  Categoría: {category}")
    print(f"   📏 Contexto: {len(context)} caracteres")
    
    try:
        response, tokens = llm_service.generate_response(
            user_message=prompt,
            context=""
        )
        
        print(f"   ✅ Generado ({tokens} tokens)")
        return response
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        raise

def main():
    """Script principal"""
    
    print("=" * 80)
    print("GENERADOR AUTOMÁTICO DE DOCUMENTOS SINTÉTICOS")
    print("=" * 80)
    
    # Directorios
    extracted_dir = Path("data/extracted")
    output_dir = Path("data/synthetic")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Cargar datos extraídos
    print(f"\n📂 Cargando datos extraídos de: {extracted_dir}")
    all_data = load_extracted_data(extracted_dir)
    
    if not all_data:
        print("\n❌ No hay datos para procesar")
        print("\n💡 Primero ejecuta: python backend/scripts/extract_pdfs.py")
        return
    
    print(f"✅ {len(all_data)} archivos cargados\n")
    
    # Procesar cada archivo
    generated_docs = []
    
    for item in all_data:
        filename = item['filename']
        data = item['data']
        product = data.get('product', 'unknown')
        sections = data.get('sections', {})
        full_text = data.get('full_text', '')
        
        print(f"\n{'='*80}")
        print(f"Procesando: {filename}")
        print(f"Producto: {product}")
        print(f"{'='*80}")
        
        # Generar documento sintético para cada categoría con contenido
        for category, section_data in sections.items():
            if not section_data:
                continue
            
            print(f"\n📝 Categoría: {category}")
            
            # Construir contexto relevante
            context_parts = [f"INFORMACIÓN SOBRE {category.upper()}:\n"]
            
            for item in section_data:
                context_parts.append(f"--- {item['header']} ---")
                context_parts.append(item['context'])
                context_parts.append("\n")
            
            # Agregar texto completo filtrado
            if full_text:
                # Buscar secciones relevantes en texto completo
                relevant_text = []
                for line in full_text.split('\n'):
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in category.split('_')):
                        relevant_text.append(line)
                
                if relevant_text:
                    context_parts.append("\n\nTEXTO COMPLETO RELEVANTE:\n")
                    context_parts.append('\n'.join(relevant_text[:100]))  # Primeras 100 líneas
            
            context = '\n'.join(context_parts)
            
            # Generar documento sintético
            try:
                synthetic_doc = generate_synthetic_doc(product, category, context)
                
                # Guardar
                output_file = output_dir / f"synthetic_{product}_{category}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(synthetic_doc)
                
                print(f"   ✅ Guardado en: {output_file.name}")
                
                generated_docs.append({
                    'product': product,
                    'category': category,
                    'filepath': str(output_file),
                    'size': len(synthetic_doc)
                })
                
            except Exception as e:
                print(f"   ❌ Error generando: {str(e)}")
                continue
    
    print("\n" + "=" * 80)
    print("GENERACIÓN COMPLETADA")
    print("=" * 80)
    
    print(f"\n✅ {len(generated_docs)} documentos sintéticos generados\n")
    
    for doc in generated_docs:
        print(f"  📄 {doc['product']} - {doc['category']}: {doc['size']} chars")
    
    print(f"\n📂 Documentos guardados en: {output_dir.absolute()}")
    
    print(f"""
🔄 SIGUIENTE PASO:
   Sube los documentos sintéticos a Pinecone:
   python backend/scripts/batch_upload_synthetic.py
""")

if __name__ == "__main__":
    main()
