# -*- coding: utf-8 -*-
import json
import os
from config import BASE_DIR, TEMPERATURE, DEFAULT_MODEL_TYPE

SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

class SettingsManager:
    """Gestiona la persistencia de ajustes del usuario"""
    
    def __init__(self):
        self.settings = self._load_settings()
    
    def _load_settings(self):
        """Carga ajustes desde el archivo JSON"""
        defaults = {
            "temperature": TEMPERATURE,
            "model_type": DEFAULT_MODEL_TYPE,
            "similarity_threshold": 0.40
        }
        
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Mezclar con defaults para asegurar que todas las llaves existan
                    defaults.update(loaded)
            except Exception as e:
                print(f"[ERROR] No se pudo cargar settings.json: {e}")
        
        return defaults
    
    def save(self):
        """Guarda los ajustes actuales en el archivo"""
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"[ERROR] No se pudo guardar settings.json: {e}")
            
    def get(self, key, default=None):
        """Obtiene un valor de ajuste"""
        return self.settings.get(key, default)
    
    def update(self, key, value):
        """Actualiza un ajuste y lo guarda"""
        self.settings[key] = value
        self.save()
