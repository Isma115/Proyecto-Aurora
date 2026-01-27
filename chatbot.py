#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proyecto Aurora - Chatbot con Gemma 2 2B, RAG y Memoria a Largo Plazo
=====================================================================

Punto de entrada principal de la aplicación.
El modelo se descarga automáticamente en la primera ejecución.

Características:
- LLM: Gemma 2 2B (modelo local, sin servidor)
- RAG: Búsqueda de contexto en archivos .txt (umbral 60%)
- Memoria: Resúmenes automáticos cada 4 mensajes
- UI: Interfaz moderna con tkinter

Uso:
    python chatbot.py

Requisitos:
    pip install llama-cpp-python
"""

import sys
import os

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    missing = []
    
    try:
        import requests
    except ImportError:
        # requests no es estrictamente necesario con el nuevo código
        pass
    
    try:
        from llama_cpp import Llama
    except ImportError:
        missing.append("llama-cpp-python")
    
    if missing:
        print("=" * 50)
        print("❌ Faltan dependencias:")
        print()
        for dep in missing:
            print(f"   - {dep}")
        print()
        print("Instálalas con:")
        print(f"   pip install {' '.join(missing)}")
        print("=" * 50)
        return False
    
    return True


def main():
    """Función principal"""
    print("=" * 50)
    print("🌌 Proyecto Aurora - Local")
    print("   RAG & Memoria a Largo Plazo")
    print("=" * 50)
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias...")
    if not check_dependencies():
        print("\n⛔ No se puede iniciar sin las dependencias.")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    print("✅ Dependencias OK")
    
    # Importar módulos
    from chat_engine import ChatEngine
    from ui_components import ChatWindow
    
    # Inicializar el motor de chat
    print("\n🔧 Creando motor de chat...")
    chat_engine = ChatEngine()
    
    # Mostrar estadísticas RAG
    stats = chat_engine.get_stats()
    print(f"\n📊 Base de conocimiento:")
    print(f"   - Documentos: {stats['rag']['documents']}")
    print(f"   - Fragmentos: {stats['rag']['chunks']}")
    
    # Iniciar interfaz gráfica
    print("\n🚀 Iniciando interfaz gráfica...")
    print("   (El modelo se descargará automáticamente si es necesario)")
    
    app = ChatWindow(chat_engine)
    app.mainloop()


if __name__ == "__main__":
    main()
