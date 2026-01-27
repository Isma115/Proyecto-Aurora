# -*- coding: utf-8 -*-
"""
Motor de Chat
Coordinador principal del chatbot
"""

from ollama_client import LocalLLMClient
from rag_engine import RAGEngine
from memory_manager import MemoryManager
from conversation_manager import ConversationManager
from config import SUMMARY_INTERVAL, SIMILARITY_THRESHOLD
from settings_manager import SettingsManager


class ChatEngine:
    """Coordinador principal que integra todos los componentes del chatbot"""
    
    def __init__(self, on_status_change=None):
        self.settings = SettingsManager()
        self.llm = LocalLLMClient()
        self.rag = RAGEngine()
        self.memory = MemoryManager()
        self.conversation_manager = ConversationManager()
        
        # Aplicar ajustes guardados
        self.llm.set_temperature(self.settings.get("temperature"))
        self.llm.model_type = self.settings.get("model_type")
        
        # Iniciar nueva conversación
        self.conversation_manager.create_conversation()
        
        # Limpiar memorias inválidas al inicio
        self.memory.cleanup_memories()
        
        self.conversation_history = []
        self.message_count = 0
        self.on_status_change = on_status_change
        self._initialized = False
    
    def update_status(self, status):
        """Actualiza el estado si hay callback"""
        if self.on_status_change:
            self.on_status_change(status)
    
    def initialize(self, progress_callback=None):
        """Inicializa el motor (descarga modelo si es necesario)"""
        self.update_status("Preparándome...")
        success = self.llm.initialize(progress_callback=progress_callback)
        self._initialized = success
        if success:
            self.update_status("Listo")
        else:
            self.update_status("Error al inicializar modelo")
        return success
    
    def is_model_downloaded(self):
        """Verifica si el modelo ya está descargado"""
        return self.llm.is_model_downloaded()
    
    def is_ready(self):
        """Verifica si el sistema está listo"""
        return self._initialized and self.llm.is_available()
    
    def process_message(self, user_input, stream_callback=None):
        """
        Procesa un mensaje del usuario.
        """
        if not self.is_ready():
            return "Error: El modelo no está listo. Inicializa primero.", False
        
        # Limpiar memorias inválidas antes de procesar
        self.memory.cleanup_memories()

        # 0. Guardar mensaje del usuario INMEDIATAMENTE para asegurar persistencia
        print(f"[DEBUG] Guardando mensaje usuario: {user_input[:30]}...")
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        try:
            self.conversation_manager.save_message("user", user_input)
            print("[DEBUG] Mensaje usuario guardado en JSON")
        except Exception as e:
            print(f"[ERROR] Falló guardado de mensaje usuario: {e}")
        
        # Actualizar estado
        self.update_status("Recordando...")
        
        # 1. Buscar contexto RAG
        threshold = self.settings.get("similarity_threshold", SIMILARITY_THRESHOLD)
        print(f"[DEBUG] Usando threshold RAG: {threshold}")
        rag_context, similarity = self.rag.get_context(user_input, threshold)
        
        # 2. RAG obtenido
        
        # (Paso 3 eliminado, ya se hizo en paso 0)
        
        # 4. Generar respuesta
        self.update_status("Pensando...")
        
        if stream_callback:
            # Ya no pasamos system_context separado (memoria), todo va por RAG filtrado
            response = self.llm.chat_stream(
                self.conversation_history,
                system_context="", 
                user_context=rag_context if rag_context else "",
                callback=stream_callback
            )
        else:
            response = self.llm.chat(
                self.conversation_history,
                system_context="",
                user_context=rag_context if rag_context else ""
            )
        
        # 5. Guardar respuesta del asistente
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        self.conversation_manager.save_message("assistant", response)
        
        # 6. Incrementar contador y verificar si toca resumen
        self.message_count += 1
        print(f"\n[DEBUG] Contador mensajes: {self.message_count} (Intervalo: {SUMMARY_INTERVAL})")
        
        if self.should_generate_summary():
            print("[DEBUG] ¡Hora de generar resumen!")
            self.update_status("Guardando lo nuestro...")
            success = self.generate_and_save_summary()
            print(f"[DEBUG] Resultado generación resumen: {success}")
        
        self.update_status("Listo")
        
        return response, rag_context is not None, similarity
    
    def should_generate_summary(self):
        """Verifica si es momento de generar un resumen"""
        should = self.message_count > 0 and self.message_count % SUMMARY_INTERVAL == 0
        if should:
            print(f"[DEBUG] should_generate_summary = True ({self.message_count} % {SUMMARY_INTERVAL} == 0)")
        return should
    
    def generate_and_save_summary(self):
        """Genera y guarda un resumen de la conversación reciente"""
        if len(self.conversation_history) < 2:
            print("[DEBUG] No hay suficiente historial para resumir")
            return
        
        # Tomar los últimos mensajes para el resumen
        recent_messages = self.conversation_history[-SUMMARY_INTERVAL * 2:]
        print(f"[DEBUG] Resumiendo {len(recent_messages)} mensajes...")
        
        # Generar resumen
        summary = self.llm.generate_summary(recent_messages)
        print(f"[DEBUG] Resumen generado (preview): {summary[:50]}...")
        
        if summary and not summary.startswith("Error"):
            # Guardar en memoria
            filepath = self.memory.save_summary(summary)
            print(f"[DEBUG] Resumen guardado en: {filepath}")
            
            # Recargar RAG para incluir nueva memoria
            self.rag.load_documents()
            print("[DEBUG] RAG recargado con nuevos recuerdos")
            return True
        else:
            print(f"[DEBUG] Error generando resumen: {summary}")
        
        return False
    
    def clear_conversation(self):
        """Inicia una nueva conversación (limpia el historial actual en memoria)"""
        self.conversation_history = []
        self.message_count = 0
        self.conversation_manager.create_conversation()
    
    def new_conversation(self):
        """Alias para clear_conversation + create_conversation explícito"""
        self.clear_conversation()
        
    def load_conversation(self, conversation_id):
        """Carga una conversación anterior"""
        data = self.conversation_manager.load_conversation(conversation_id)
        if data:
            self.conversation_history = []
            for msg in data.get("messages", []):
                # Validar formato de mensajes para asegurar compatibilidad con LLM
                if "role" in msg and "content" in msg:
                    self.conversation_history.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            self.message_count = len([m for m in self.conversation_history if m["role"] == "user"])
            return True
        return False
        
    def list_conversations(self):
        """Lista todas las conversaciones"""
        return self.conversation_manager.list_conversations()
        
    def delete_conversation(self, conversation_id):
        """Elimina una conversación"""
        return self.conversation_manager.delete_conversation(conversation_id)

    def reload_knowledge(self):
        """Recarga la base de conocimiento"""
        self.rag.reload()
    
    def get_stats(self):
        """Obtiene estadísticas del sistema"""
        current_id = self.conversation_manager.current_conversation_id
        return {
            'messages': len(self.conversation_history),
            'message_count': self.message_count,
            'rag': self.rag.get_stats(),
            'memory': self.memory.get_stats(),
            'model_ready': self.is_ready(),
            'current_conversation': current_id,
            'temperature': self.llm.temperature
        }

    def set_temperature(self, value):
        """Actualiza la temperatura del modelo y guarda"""
        self.llm.set_temperature(value)
        self.settings.update("temperature", float(value))

    def switch_model(self, model_type, progress_callback=None):
        """Cambia el tipo de modelo (Instruct/Base) y guarda"""
        success = self.llm.initialize(model_type, progress_callback)
        if success:
            self.settings.update("model_type", model_type)
        return success
