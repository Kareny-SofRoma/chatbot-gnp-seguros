#!/usr/bin/env python3
"""
Script to process and cache FAQ answers.
Run this script once to generate answers for all FAQs.
"""
import requests
import json
import sys
from pathlib import Path

# API endpoint
API_BASE_URL = "http://localhost:8000"
FAQ_ENDPOINT = f"{API_BASE_URL}/api/v1/faq/batch-process"

def process_faqs(json_file_path: str):
    """
    Read FAQs from JSON file and send them to the API for processing.
    """
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        
        print(f"📚 Cargando {len(faq_data['questions'])} preguntas frecuentes...")
        print(f"📂 Categoría: {faq_data['category']}\n")
        
        # Send to API
        print("🔄 Procesando FAQs (esto puede tardar varios minutos)...\n")
        
        response = requests.post(
            FAQ_ENDPOINT,
            json=faq_data,
            headers={"Content-Type": "application/json"},
            timeout=600  # 10 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ ¡Proceso completado!")
            print(f"   ✓ Procesadas exitosamente: {result['processed']}/{result['total']}")
            print(f"   ✗ Fallidas: {result['failed']}/{result['total']}")
            
            if result['failed'] > 0:
                print(f"\n⚠️  Algunas FAQs fallaron. Verifica los logs del backend.")
            
            print(f"\n📊 Resumen:")
            for faq in result['faqs'][:5]:  # Show first 5
                print(f"   • {faq['question'][:60]}...")
            
            if len(result['faqs']) > 5:
                print(f"   ... y {len(result['faqs']) - 5} más")
            
            return True
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {json_file_path}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: No se pudo conectar al API en {API_BASE_URL}")
        print(f"   Asegúrate de que el backend esté corriendo (docker-compose up)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Error: Timeout esperando respuesta del API")
        print(f"   El procesamiento puede tomar tiempo. Verifica los logs del backend.")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("  SOIA - Procesador de Preguntas Frecuentes")
    print("=" * 60)
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent
    json_file = script_dir / "faqs_gmm.json"
    
    if not json_file.exists():
        print(f"❌ No se encontró el archivo: {json_file}")
        print(f"   Crea el archivo faqs_gmm.json en: {script_dir}")
        sys.exit(1)
    
    success = process_faqs(str(json_file))
    
    if success:
        print(f"\n🎉 Las FAQs están listas para usar!")
        print(f"   Ahora los usuarios verán respuestas instantáneas.")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
