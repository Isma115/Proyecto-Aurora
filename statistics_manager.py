# -*- coding: utf-8 -*-
import json
import os
from config import BASE_DIR

STATISTICS_FILE = os.path.join(BASE_DIR, "statistics.json")

class StatisticsManager:
    """Gestiona la persistencia de estadísticas del uso del chatbot"""
    
    def __init__(self):
        self.stats = self._load_stats()
    
    def _load_stats(self):
        """Carga estadísticas desde el archivo JSON"""
        defaults = {
            "total_user_messages": 0
        }
        
        if os.path.exists(STATISTICS_FILE):
            try:
                with open(STATISTICS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    defaults.update(loaded)
            except Exception as e:
                print(f"[ERROR] No se pudo cargar statistics.json: {e}")
        
        return defaults
    
    def save(self):
        """Guarda las estadísticas actuales en el archivo"""
        try:
            with open(STATISTICS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=4)
        except Exception as e:
            print(f"[ERROR] No se pudo guardar statistics.json: {e}")
            
    def get_total_user_messages(self):
        """Obtiene el número total de mensajes enviados por el usuario"""
        return self.stats.get("total_user_messages", 0)
    
    def increment_user_messages(self):
        """Incrementa el contador de mensajes de usuario y guarda"""
        self.stats["total_user_messages"] = self.stats.get("total_user_messages", 0) + 1
        self.save()
        return self.stats["total_user_messages"]
