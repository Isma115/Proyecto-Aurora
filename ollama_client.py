# -*- coding: utf-8 -*-
"""
Cliente de modelo local usando llama-cpp-python
Ejecuta Gemma 2 2B directamente sin servidor
"""

import os
import sys
import ssl
import threading
from config import MODELS_DIR, MAX_TOKENS, CONTEXT_LENGTH, TEMPERATURE, MODELS_CONFIG, DEFAULT_MODEL_TYPE
from settings_manager import SettingsManager

# Variable global para el modelo
_model = None
_model_lock = threading.Lock()

# Fix para SSL en macOS
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except ImportError:
    pass

# Crear contexto SSL sin verificación (fallback para macOS)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def download_model(model_url, model_path, progress_callback=None):
    """Descarga el modelo si no existe"""
    if os.path.exists(model_path):
        return True
    
    # Obtener el nombre del archivo desde la ruta
    model_filename = os.path.basename(model_path)
    
    print(f"📥 Descargando modelo {model_filename}...")
    print(f"   Esto puede tardar varios minutos (aprox. 1.5GB)")
    print(f"   URL: {model_url}")
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Intentar con requests primero (mejor manejo de SSL)
    try:
        import requests
        print("   Usando requests para descarga...")
        
        response = requests.get(model_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        chunk_size = 8192
        
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        
                        if progress_callback:
                            progress_callback(percent, mb_downloaded, mb_total)
                        else:
                            sys.stdout.write(f"\r   Progreso: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
                            sys.stdout.flush()
        
        print("\n✅ Modelo descargado correctamente")
        return True
        
    except ImportError:
        print("   requests no disponible, usando urllib...")
    except Exception as e:
        print(f"   Error con requests: {e}")
        print("   Intentando con urllib...")
        if os.path.exists(model_path):
            os.remove(model_path)
    
    # Fallback a urllib con SSL deshabilitado
    try:
        import urllib.request
        
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, (downloaded / total_size) * 100) if total_size > 0 else 0
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            
            if progress_callback:
                progress_callback(percent, mb_downloaded, mb_total)
            else:
                sys.stdout.write(f"\r   Progreso: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
                sys.stdout.flush()
        
        # Usar contexto SSL sin verificación
        urllib.request.urlretrieve(model_url, model_path, reporthook=report_progress, context=ssl_context)
        print("\n✅ Modelo descargado correctamente")
        return True
    except Exception as e:
        print(f"\n❌ Error descargando modelo: {e}")
        print("\n💡 Solución alternativa:")
        print(f"   Descarga manualmente el modelo desde:")
        print(f"   {model_url}")
        print(f"   Y colócalo en: {model_path}")
        if os.path.exists(model_path):
            os.remove(model_path)
        return False


# Diccionario para almacenar modelos cargados
_loaded_models = {}
_model_lock = threading.Lock()

def get_model(model_path):
    """Obtiene o carga el modelo específico"""
    global _loaded_models
    
    with _model_lock:
        if model_path not in _loaded_models:
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Modelo no encontrado en {model_path}."
                )
            
            try:
                from llama_cpp import Llama
                
                print(f"🔄 Cargando modelo desde {os.path.basename(model_path)}...")
                _loaded_models[model_path] = Llama(
                    model_path=model_path,
                    n_ctx=CONTEXT_LENGTH,
                    n_threads=4,
                    verbose=False
                )
                print("✅ Modelo cargado correctamente")
            except ImportError:
                raise ImportError(
                    "llama-cpp-python no está instalado."
                )
        
        return _loaded_models[model_path]


class LocalLLMClient:
    """Cliente para el modelo local Gemma 2 2B"""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.model = None
        self._is_ready = False
        self.temperature = self.settings.get("temperature", TEMPERATURE)
        self.model_type = self.settings.get("model_type", DEFAULT_MODEL_TYPE)

    def set_temperature(self, value):
        """Actualiza la temperatura del modelo"""
        self.temperature = float(value)
        print(f"[DEBUG] Temperatura actualizada a: {self.temperature}")
    
    def initialize(self, model_type=None, progress_callback=None):
        """Inicializa el modelo (descarga si es necesario)"""
        if model_type:
            self.model_type = model_type
            
        config = MODELS_CONFIG[self.model_type]
        model_path = os.path.join(MODELS_DIR, config["filename"])
        model_url = config["url"]

        # Verificar si el modelo existe
        if not os.path.exists(model_path):
            success = download_model(model_url, model_path, progress_callback)
            if not success:
                return False
        
        # Cargar el modelo
        try:
            self.model = get_model(model_path)
            self._is_ready = True
            return True
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            return False
    
    def is_available(self):
        """Verifica si el modelo está disponible"""
        return self._is_ready and self.model is not None
    
    def is_model_downloaded(self, model_type=None):
        """Verifica si el modelo ya está descargado"""
        m_type = model_type or self.model_type
        filename = MODELS_CONFIG[m_type]["filename"]
        path = os.path.join(MODELS_DIR, filename)
        return os.path.exists(path)
    
    def generate(self, prompt, context="", system_prompt=""):
        """Genera una respuesta del modelo"""
        if not self.is_available():
            return "Error: Modelo no disponible"
        
        # Construir el prompt completo
        full_prompt = self._build_prompt(prompt, context, system_prompt)
        
        try:
            output = self.model(
                full_prompt,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                stop=["Usuario:", "\n\nUsuario:", "<end_of_turn>"],
                echo=False
            )
            
            response = output['choices'][0]['text'].strip()
            return response
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"
    
    def generate_stream(self, prompt, context="", system_prompt="", callback=None):
        """Genera una respuesta en streaming"""
        if not self.is_available():
            if callback:
                callback("Error: Modelo no disponible")
            return "Error: Modelo no disponible"
        
        full_prompt = self._build_prompt(prompt, context, system_prompt)
        
        try:
            full_response = ""
            for output in self.model(
                full_prompt,
                max_tokens=MAX_TOKENS,
                temperature=self.temperature,
                stop=["<end_of_turn>", "Usuario:"],
                echo=False,
                stream=True
            ):
                token = output['choices'][0]['text']
                full_response += token
                if callback:
                    callback(token)
            
            return full_response.strip()
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if callback:
                callback(error_msg)
            return error_msg
    
    def _get_system_prompt(self):
        """Lee el system prompt desde el archivo o usa el default"""
        try:
            prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.txt")
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
        except Exception as e:
            print(f"[ERROR] No se pudo leer system_prompt.txt: {e}")
        
        return "Eres Aurora, una chica joven y directa, sin adornos en tu conversación. Tu tono es equilibrado y natural. Responde siempre en Español de España."

    def _build_prompt(self, user_input, context="", system_prompt=""):
        """Construye el prompt según el tipo de modelo"""
        prompt_parts = []
        
        # System prompt
        if not system_prompt:
            system_prompt = self._get_system_prompt()
        
        if context:
            system_prompt += f"\n\nInformación de contexto relevante:\n{context}"
        
        if self.model_type == "instruct":
            # Formato Gemma 2 Instruct
            prompt_parts.append(f"<start_of_turn>user\n{system_prompt}\n\n{user_input}<end_of_turn>")
            prompt_parts.append("<start_of_turn>model\n")
        else:
            # Formato Simple para Base Model
            prompt_parts.append(f"Instrucciones:\n{system_prompt}\n\nUsuario: {user_input}\nAurora:")
        
        return "".join(prompt_parts)
    
    def generate_summary(self, conversation_history):
        """Genera un resumen de la conversación"""
        # Usar etiquetas neutras para evitar stop tokens accidentales
        conversation_text = "\n".join([
            f"{'Interlocutor' if msg['role'] == 'user' else 'Aurora'}: {msg['content']}"
            for msg in conversation_history
        ])
        
        print(f"\n[DEBUG] Generando resumen para {len(conversation_history)} mensajes")
        # print(f"[DEBUG] Contexto conversación (preview): {conversation_text[:100]}...")
        
        summary_prompt = f"""Tu tarea es crear un RESUMEN MEMORABLE de la siguiente conversación. 
Extrae HECHOS, DATOS, PREFERENCIAS y TEMAS importantes.
NO narres "el humano dijo", simplemente lista la información extraída.

Conversación:
{conversation_text}

RESUMEN DETALLADO:"""
        
        # Usar _build_prompt para formatear correctamente para Gemma 2
        full_prompt = self._build_prompt(summary_prompt, system_prompt="Eres Aurora, recordando momentos compartidos.")
        
        # print(f"[DEBUG] Prompt completo enviado al modelo (len={len(full_prompt)})")
        
        try:
            # Aumentar max_tokens y reducir stop words para evitar que corte
            output = self.model(
                full_prompt,
                max_tokens=1024, # Aumentado para resumenes largos
                temperature=0.6, # Un poco más determinista
                stop=["<end_of_turn>"], # Quitamos "Usuario:" para evitar falsos positivos
                echo=False
            )
            
            result = output['choices'][0]['text'].strip()
            print(f"[DEBUG] Resultado raw del modelo: '{result}'")
            return result
        except Exception as e:
            print(f"[DEBUG] Error en generate_summary: {e}")
            return f"Error generando resumen: {str(e)}"
    
    def _trim_history(self, messages, system_context="", user_context=""):
        """
        Recorta el historial para ajustar al límite de contexto.
        Estimación simple: 1 token ≈ 4 caracteres
        """
        # Calcular tokens base (System + Contextos + Margen)
        # Margen para la respuesta nueva y overhead de formato
        # Si MAX_TOKENS es infinito (None), reservamos un buffer razonable (ej. 1024)
        safe_max_tokens = MAX_TOKENS if MAX_TOKENS is not None else 1024
        reserved_tokens = safe_max_tokens + 100 
        
        system_len = len(system_context) if system_context else 0
        rag_len = len(user_context) if user_context else 0
        
        # System prompt base
        base_prompt_len = len(self._get_system_prompt())
        
        # Tokens estimados ocupados por lo que NO podemos borrar (System + RAG)
        # 1 token aprox 4 caracteres
        used_tokens = (base_prompt_len + system_len + rag_len) / 4
        
        available_tokens = CONTEXT_LENGTH - reserved_tokens - used_tokens
        
        if available_tokens <= 0:
            print("[WARNING] Contexto RAG + Memorias excede el límite. Recortando...")
            return []
            
        trimmed_messages = []
        current_tokens = 0
        
        # Iterar desde el final (mensajes más recientes son más importantes)
        for msg in reversed(messages):
            msg_len = len(msg['content'])
            msg_tokens = (msg_len / 4) + 10 # +10 por overhead de etiquetas <start_of_turn>...
            
            if current_tokens + msg_tokens <= available_tokens:
                trimmed_messages.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
                
        if len(trimmed_messages) < len(messages):
            print(f"[INFO] Historial recortado: {len(messages)} -> {len(trimmed_messages)} mensajes")
            
        return trimmed_messages

    def chat(self, messages, system_context="", user_context=""):
        """
        Chat con historial de mensajes.
        
        Args:
            messages: Lista de diccionarios con el historial
            system_context: Contexto estable (Memorias) para el System Prompt
            user_context: Contexto dinámico (RAG) para el último mensaje de usuario
        """
        # 1. Recortar historial para que quepa
        history_window = self._trim_history(messages[:-1], system_context, user_context)
        
        system_prompt = self._get_system_prompt()
        if system_context:
            system_prompt += f"\n\nContexto de Memoria a Largo Plazo:\n{system_context}"
        
        # Construir prompt completo con historial
        full_prompt = f"Instrucciones:\n{system_prompt}\n\n"
        
        # Añadir historial (excepto el último que se añade al final)
        for msg in history_window:
            role = "Usuario" if msg['role'] == 'user' else "Aurora"
            content = msg['content']
            full_prompt += f"{role}: {content}\n"
            
        # Añadir mensaje actual con contexto RAG si existe
        last_user_msg = messages[-1]['content'] if messages else ""
        if user_context:
            last_user_msg = f"Información relevante encontrada:\n{user_context}\n\nPregunta del usuario:\n{last_user_msg}"
            
        full_prompt += f"Usuario: {last_user_msg}\nAurora:"
        
        try:
            output = self.model(
                full_prompt,
                max_tokens=MAX_TOKENS,
                temperature=self.temperature,
                stop=["<end_of_turn>", "Usuario:"],
                echo=False
            )
            
            return output['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_stream(self, messages, system_context="", user_context="", callback=None):
        """Chat con streaming y contexto separado"""
        # 1. Recortar historial para que quepa
        history_window = self._trim_history(messages[:-1], system_context, user_context)

        system_prompt = self._get_system_prompt()
        if system_context:
            system_prompt += f"\n\nContexto de Memoria a Largo Plazo:\n{system_context}"
        
        # Construir prompt completo con historial
        if self.model_type == "instruct":
            full_prompt = f"<start_of_turn>user\n{system_prompt}\n\n"
            for msg in history_window:
                role = "user" if msg['role'] == 'user' else "model"
                full_prompt += f"<start_of_turn>{role}\n{msg['content']}<end_of_turn>\n"
        else:
            full_prompt = f"Instrucciones:\n{system_prompt}\n\n"
            for msg in history_window:
                role = "Usuario" if msg['role'] == 'user' else "Aurora"
                full_prompt += f"{role}: {msg['content']}\n"
        
        last_user_msg = messages[-1]['content'] if messages else ""
        
        # DEBUG: Mostrar qué contextos se están usando
        print(f"\n[DEBUG-LLM] user_context (RAG) presente: {bool(user_context)}")
        print(f"[DEBUG-LLM] system_context (Memorias) presente: {bool(system_context)}")
        if user_context:
            print(f"[DEBUG-LLM] ⚠️ AÑADIENDO RAG AL PROMPT: {user_context[:100]}...")
        
        if user_context:
            last_user_msg = f"Información relevante encontrada:\n{user_context}\n\nPregunta del usuario:\n{last_user_msg}"

        if self.model_type == "instruct":
            full_prompt += f"<start_of_turn>user\n{last_user_msg}<end_of_turn>\n<start_of_turn>model\n"
        else:
            full_prompt += f"Usuario: {last_user_msg}\nAurora:"
        
        try:
            full_response = ""
            for output in self.model(
                full_prompt,
                max_tokens=MAX_TOKENS,
                temperature=self.temperature,
                stop=["<end_of_turn>", "Usuario:"],
                echo=False,
                stream=True
            ):
                token = output['choices'][0]['text']
                full_response += token
                if callback:
                    callback(token)
            
            return full_response.strip()
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if callback:
                callback(error_msg)
            return error_msg


# Alias para compatibilidad
OllamaClient = LocalLLMClient
