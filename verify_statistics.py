# -*- coding: utf-8 -*-
"""
Script de verificación para el sistema de estadísticas.
Prueba la lógica de conteo y persistencia sin levantar toda la UI.
"""
import os
import shutil
from statistics_manager import StatisticsManager
from config import BASE_DIR

TEST_STATS_FILE = os.path.join(BASE_DIR, "statistics.json")
BACKUP_STATS_FILE = os.path.join(BASE_DIR, "statistics.json.bak")

def setup():
    """Backup del archivo real si existe"""
    if os.path.exists(TEST_STATS_FILE):
        shutil.copy(TEST_STATS_FILE, BACKUP_STATS_FILE)
        # Resetear para test
        try:
           os.remove(TEST_STATS_FILE)
        except:
           pass

def teardown():
    """Restaurar backup"""
    if os.path.exists(TEST_STATS_FILE):
        os.remove(TEST_STATS_FILE)
        
    if os.path.exists(BACKUP_STATS_FILE):
        shutil.move(BACKUP_STATS_FILE, TEST_STATS_FILE)

def test_statistics_logic():
    print("Testing StatisticsManager...")
    
    # 1. Crear manager nuevo (debe empezar en 0 si no hay archivo)
    mgr = StatisticsManager()
    initial = mgr.get_total_user_messages()
    print(f"Initial count: {initial}")
    assert initial == 0, f"Expected 0, got {initial}"
    
    # 2. Incrementar
    new_count = mgr.increment_user_messages()
    print(f"Count after increment: {new_count}")
    assert new_count == 1, f"Expected 1, got {new_count}"
    
    # 3. Persistencia
    # Crear nueva instancia, debe cargar el valor guardado
    mgr2 = StatisticsManager()
    loaded_count = mgr2.get_total_user_messages()
    print(f"Loaded count from new instance: {loaded_count}")
    assert loaded_count == 1, f"Expected 1, got {loaded_count}"
    
    print("✅ Statistics Logic Verified Successfully!")

if __name__ == "__main__":
    try:
        setup()
        test_statistics_logic()
    except AssertionError as e:
        print(f"❌ Verification Failed: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        teardown()
