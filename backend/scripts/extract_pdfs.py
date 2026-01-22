"""
Extractor inteligente de texto de PDFs

Este script extrae texto de PDFs y detecta secciones automáticamente
para facilitar la creación de documentos sintéticos.

Uso:
    python backend/scripts/extract_pdfs.py

Coloca tus PDFs en: backend/data/pdfs_to_process/
"""

import sys
import os
from pathlib import Path
import re
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import PyPDF2
except ImportError:
    print("❌ ERROR: PyPDF2 no está instalado")
    print("Instala con: pip install PyPDF2")
    sys.exit(1)

class PDFExtractor:
    def __init__(self):
        self.sections_detected = []
        self.product_name = None
        self.category = None
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrae todo el texto de un PDF"""
        print(f"📄 Extrayendo texto de: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                total_pages = len(pdf_reader.pages)
                
                for i, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    text += f"\n\n--- PÁGINA {i} DE {total_pages} ---\n\n{page_text}"
                    print(f"   ✓ Página {i}/{total_pages} extraída")
                
                return text
        except Exception as e:
            print(f"❌ Error extrayendo PDF: {str(e)}")
            raise
    
    def detect_product(self, text: str) -> str:
        """Detecta el nombre del producto en el texto"""
        products = {
            'versátil': ['versatil', 'versátil'],
            'premium': ['premium'],
            'platino': ['platino'],
            'conexión gnp': ['conexión gnp', 'conexion gnp'],
            'auto más': ['auto más', 'auto mas'],
            'auto élite': ['auto élite', 'auto elite'],
            'hogar versátil': ['hogar versátil', 'hogar versatil'],
            'negocio protegido': ['negocio protegido'],
            'alta especialidad': ['alta especialidad'],
            'enlace internacional': ['enlace internacional'],
            'producto internacional': ['producto internacional', 'linea azul internacional', 'línea azul internacional'],
            'vip': ['vip ', ' vip', 'vip\n', 'vip.']
        }
        
        text_lower = text.lower()
        
        for product, keywords in products.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return product
        
        return "unknown"
    
    def detect_sections(self, text: str) -> dict:
        """Detecta secciones relevantes en el texto"""
        sections = {
            'periodos_espera': [],
            'coberturas': [],
            'deducibles': [],
            'coaseguros': [],
            'exclusiones': [],
            'requisitos': [],
            'sumas_aseguradas': [],
            'indemnizaciones': []
        }
        
        # Patrones para detectar secciones
        patterns = {
            'periodos_espera': [
                r'periodo[s]?\s+de\s+espera',
                r'tiempo[s]?\s+de\s+espera',
                r'\d+\s+meses?\s+de\s+espera'
            ],
            'coberturas': [
                r'cobertura[s]?',
                r'beneficio[s]?',
                r'servicio[s]?\s+cubierto[s]?',
                r'qué\s+cubre',
                r'incluye'
            ],
            'deducibles': [
                r'deducible[s]?',
                r'monto\s+deducible'
            ],
            'coaseguros': [
                r'coaseguro[s]?',
                r'porcentaje\s+de\s+coaseguro'
            ],
            'exclusiones': [
                r'exclusion[es]?',
                r'no\s+cubre',
                r'excepto',
                r'limitacion[es]?'
            ],
            'requisitos': [
                r'requisito[s]?',
                r'documento[s]?\s+necesario[s]?',
                r'debe\s+presentar'
            ],
            'sumas_aseguradas': [
                r'suma[s]?\s+asegurada[s]?',
                r'límite[s]?',
                r'tope[s]?',
                r'monto[s]?\s+máximo[s]?'
            ],
            'indemnizaciones': [
                r'indemnización[es]?',
                r'pago[s]?',
                r'compensación[es]?'
            ]
        }
        
        # Detectar secciones
        lines = text.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            if not line_lower:
                continue
            
            # Detectar inicio de sección
            for section_name, section_patterns in patterns.items():
                for pattern in section_patterns:
                    if re.search(pattern, line_lower):
                        current_section = section_name
                        # Capturar contexto (siguiente 50 líneas)
                        context = '\n'.join(lines[i:min(i+50, len(lines))])
                        sections[section_name].append({
                            'line_number': i,
                            'header': line.strip(),
                            'context': context[:1000]  # Primeros 1000 chars
                        })
                        break
        
        return sections
    
    def generate_extraction_report(self, pdf_path: str, text: str, sections: dict, product: str) -> str:
        """Genera reporte de extracción"""
        report = f"""
{'='*80}
REPORTE DE EXTRACCIÓN - {Path(pdf_path).name}
{'='*80}

📦 PRODUCTO DETECTADO: {product}
📏 TAMAÑO: {len(text)} caracteres
📄 PÁGINAS: {text.count('--- PÁGINA')}

{'='*80}
SECCIONES DETECTADAS
{'='*80}

"""
        
        for section_name, section_data in sections.items():
            if section_data:
                report += f"\n✓ {section_name.upper().replace('_', ' ')}: {len(section_data)} ocurrencias\n"
                for i, item in enumerate(section_data[:3], 1):  # Primeras 3
                    report += f"  {i}. Línea {item['line_number']}: {item['header'][:80]}...\n"
        
        report += f"\n{'='*80}\n"
        return report

def main():
    """Script principal"""
    
    print("=" * 80)
    print("EXTRACTOR INTELIGENTE DE PDFs")
    print("=" * 80)
    
    # Directorio de PDFs
    pdf_dir = Path("data/pdfs_to_process")
    output_dir = Path("data/extracted")
    
    # Crear directorios si no existen
    pdf_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Buscar PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"\n❌ No se encontraron PDFs en: {pdf_dir}")
        print(f"\n💡 Coloca tus PDFs en: {pdf_dir.absolute()}")
        return
    
    print(f"\n📁 Encontrados {len(pdf_files)} PDFs para procesar\n")
    
    extractor = PDFExtractor()
    
    for pdf_file in pdf_files:
        print(f"\n{'='*80}")
        print(f"Procesando: {pdf_file.name}")
        print(f"{'='*80}\n")
        
        # Extraer texto
        text = extractor.extract_text_from_pdf(str(pdf_file))
        
        # Detectar producto
        product = extractor.detect_product(text)
        print(f"\n🏷️  Producto detectado: {product}")
        
        # Detectar secciones
        print(f"\n🔍 Detectando secciones...")
        sections = extractor.detect_sections(text)
        
        # Generar reporte
        report = extractor.generate_extraction_report(str(pdf_file), text, sections, product)
        
        # Guardar texto completo
        output_file = output_dir / f"{pdf_file.stem}_extracted.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\n✅ Texto guardado en: {output_file}")
        
        # Guardar reporte
        report_file = output_dir / f"{pdf_file.stem}_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Reporte guardado en: {report_file}")
        
        # Guardar secciones como JSON
        sections_file = output_dir / f"{pdf_file.stem}_sections.json"
        with open(sections_file, 'w', encoding='utf-8') as f:
            json.dump({
                'product': product,
                'sections': sections,
                'extracted_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        print(f"✅ Secciones guardadas en: {sections_file}")
        
        print(report)
    
    print("\n" + "=" * 80)
    print("EXTRACCIÓN COMPLETADA")
    print("=" * 80)
    
    print(f"""
✅ Archivos generados en: {output_dir.absolute()}

📂 Para cada PDF se generó:
   1. *_extracted.txt  - Texto completo extraído
   2. *_report.txt     - Reporte de secciones detectadas
   3. *_sections.json  - Datos estructurados de secciones

🔄 SIGUIENTE PASO:
   Ejecuta el generador de documentos sintéticos:
   python backend/scripts/generate_synthetic_docs.py
""")

if __name__ == "__main__":
    main()
