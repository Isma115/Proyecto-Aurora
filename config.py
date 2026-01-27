# -*- coding: utf-8 -*-
"""
Configuración global del Chatbot con Gemma 2 2B
"""

import os

# Rutas del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "conocimiento")
MEMORY_DIR = os.path.join(BASE_DIR, "memoria")
CONVERSATIONS_DIR = os.path.join(BASE_DIR, "conversaciones")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Configuración de modelos disponibles
MODELS_CONFIG = {
    "instruct": {
        "filename": "gemma-2-2b-it-Q4_K_M.gguf",
        "url": "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf"
    },
    "base": {
        "filename": "gemma-2-2b-Q4_K_M.gguf",
        "url": "https://huggingface.co/tensorblock/gemma-2-2b-GGUF/resolve/main/gemma-2-2b-Q4_K_M.gguf"
    }
}

# Modelo por defecto
DEFAULT_MODEL_TYPE = "base"

MODEL_FILENAME = MODELS_CONFIG[DEFAULT_MODEL_TYPE]["filename"]
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_FILENAME)
MODEL_URL = MODELS_CONFIG[DEFAULT_MODEL_TYPE]["url"]

# Configuración del modelo
MAX_TOKENS = None  # Infinito (hasta llenar contexto)
CONTEXT_LENGTH = 4096
TEMPERATURE = 0.1

# Configuración RAG
SIMILARITY_THRESHOLD = 0.40  # 40% de coincidencia mínima para usar contexto RAG
CHUNK_SIZE = 1500  # Caracteres por fragmento
MAX_RAG_RESULTS = 3  # Volvemos a 3 para evitar saturar el contexto
MIN_RAG_QUERY_LENGTH = 8  # Longitud mínima para buscar contexto

# Configuración de memoria
SUMMARY_INTERVAL = 4  # Generar resumen cada 4 mensajes
MAX_MEMORY_FILE_SIZE = 1024 * 1024  # 1MB en bytes

# Crear directorios si no existen
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
