# -*- coding: utf-8 -*-
import os
import json
import uuid
from datetime import datetime
from config import CONVERSATIONS_DIR

class ConversationManager:
    """Gestor de historial de conversaciones (Threads)"""
    
    def __init__(self):
        self.conversations_dir = CONVERSATIONS_DIR
        self.current_conversation_id = None
        self.current_conversation_data = None
    
    def create_conversation(self):
        """Crea una nueva conversación vacía"""
        conv_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        self.current_conversation_id = conv_id
        self.current_conversation_data = {
            "id": conv_id,
            "title": f"Conversación {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "created_at": timestamp,
            "updated_at": timestamp,
            "messages": []
        }
        
        self._save_to_disk()
        return self.current_conversation_data

    def save_message(self, role, content):
        """Guarda un mensaje en la conversación actual"""
        print(f"[DEBUG-CM] save_message llamado. Role: {role}, Content len: {len(content)}")
        if not self.current_conversation_id:
            print("[DEBUG-CM] No hay ID, creando conversación...")
            self.create_conversation()
            
        timestamp = datetime.now().isoformat()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        self.current_conversation_data["messages"].append(message)
        self.current_conversation_data["updated_at"] = timestamp
        
        # Actualizar título si es el primer mensaje del usuario
        if len(self.current_conversation_data["messages"]) <= 2 and role == "user":
            # Usar primeros 30 caracteres
            safe_title = content[:30].strip() + "..."
            self.current_conversation_data["title"] = safe_title
            
        self._save_to_disk()
        print(f"[DEBUG-CM] Guardado en disco exitoso. Total mensajes: {len(self.current_conversation_data['messages'])}")

    def update_conversation_history(self, history):
        """Actualiza todo el historial de la conversación actual (sincronizar con chat_engine)"""
        if not self.current_conversation_id:
            self.create_conversation()
            
        self.current_conversation_data["messages"] = history
        self.current_conversation_data["updated_at"] = datetime.now().isoformat()
        self._save_to_disk()

    def load_conversation(self, conversation_id):
        """Carga una conversación específica por ID"""
        filepath = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        
        if not os.path.exists(filepath):
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.current_conversation_id = data["id"]
                self.current_conversation_data = data
                return data
        except Exception as e:
            print(f"Error cargando conversación {conversation_id}: {e}")
            return None

    def list_conversations(self):
        """Lista todas las conversaciones disponibles, ordenadas por fecha de actualización"""
        conversations = []
        
        if not os.path.exists(self.conversations_dir):
            return []
            
        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.conversations_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        conversations.append({
                            "id": data.get("id"),
                            "title": data.get("title", "Sin título"),
                            "updated_at": data.get("updated_at", ""),
                            "message_count": len(data.get("messages", []))
                        })
                except Exception:
                    continue
        
        # Ordenar por fecha de actualización (más reciente primero)
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return conversations

    def delete_conversation(self, conversation_id):
        """Elimina una conversación"""
        filepath = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            if self.current_conversation_id == conversation_id:
                self.current_conversation_id = None
                self.current_conversation_data = None
            return True
        return False

    def _save_to_disk(self):
        """Escribe la conversación actual al disco"""
        if not self.current_conversation_data:
            return
            
        filepath = os.path.join(self.conversations_dir, f"{self.current_conversation_id}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_conversation_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando conversación: {e}")
