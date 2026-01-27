# -*- coding: utf-8 -*-
"""
Gestor de Memoria a Largo Plazo
Almacena resúmenes de conversaciones en archivos de texto
"""

import os
from datetime import datetime
from config import MEMORY_DIR, MAX_MEMORY_FILE_SIZE


class MemoryManager:
    """Gestiona la memoria a largo plazo del chatbot"""
    
    def __init__(self, memory_dir=MEMORY_DIR):
        self.memory_dir = memory_dir
        self.ensure_directory()
    
    def ensure_directory(self):
        """Asegura que el directorio de memoria existe"""
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
    
    def get_memory_files(self):
        """Obtiene lista de archivos de memoria ordenados"""
        files = []
        for filename in os.listdir(self.memory_dir):
            if filename.startswith('memoria_') and filename.endswith('.txt'):
                filepath = os.path.join(self.memory_dir, filename)
                files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': os.path.getsize(filepath)
                })
        
        # Ordenar por nombre (que incluye número)
        files.sort(key=lambda x: x['filename'])
        return files
    
    def get_current_file(self):
        """Obtiene el archivo de memoria actual (el último que no excede el límite)"""
        files = self.get_memory_files()
        
        if not files:
            return self.create_new_file()
        
        # Verificar el último archivo
        last_file = files[-1]
        if last_file['size'] < MAX_MEMORY_FILE_SIZE:
            return last_file['filepath']
        
        # Si excede el límite, crear nuevo
        return self.create_new_file()
    
    def create_new_file(self):
        """Crea un nuevo archivo de memoria"""
        files = self.get_memory_files()
        next_number = len(files) + 1
        filename = f"memoria_{next_number:03d}.txt"
        filepath = os.path.join(self.memory_dir, filename)
        
        # Crear archivo vacío con encabezado
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Memoria del Chatbot - Archivo {next_number}\n")
            f.write(f"# Creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
        
        return filepath
    
    def save_summary(self, summary):
        """Guarda un resumen en el archivo de memoria actual"""
        filepath = self.get_current_file()
        
        # Verificar si el nuevo contenido excederá el límite
        current_size = os.path.getsize(filepath)
        new_content = f"\n--- Resumen [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ---\n{summary}\n"
        new_size = current_size + len(new_content.encode('utf-8'))
        
        if new_size > MAX_MEMORY_FILE_SIZE:
            # Crear nuevo archivo
            filepath = self.create_new_file()
        
        # Añadir resumen al archivo
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(new_content)
        
        return filepath
    
    def get_all_memories(self, max_chars=2000):
        """
        Lee todas las memorias guardadas.
        Devuelve las memorias más recientes hasta un máximo de caracteres.
        """
        files = self.get_memory_files()
        
        if not files:
            return None
        
        all_content = []
        total_chars = 0
        
        # Leer archivos en orden inverso (más recientes primero)
        for file_info in reversed(files):
            try:
                with open(file_info['filepath'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extraer solo los resúmenes (no los encabezados)
                    summaries = self.extract_summaries(content)
                    
                    for summary in reversed(summaries):
                        if total_chars + len(summary) <= max_chars:
                            all_content.insert(0, summary)
                            total_chars += len(summary)
                        else:
                            break
                    
                    if total_chars >= max_chars:
                        break
            except Exception as e:
                print(f"Error leyendo {file_info['filename']}: {e}")
        
        if not all_content:
            return None
        
        return "\n\n".join(all_content)
    
    def extract_summaries(self, content):
        """Extrae los resúmenes de un archivo de memoria"""
        summaries = []
        current_summary = []
        in_summary = False
        
        for line in content.split('\n'):
            if line.startswith('--- Resumen [') or line.startswith('--- RECUERDO VIVIDO ['):
                if current_summary:
                    summaries.append('\n'.join(current_summary))
                current_summary = [line]
                in_summary = True
            elif in_summary:
                if line.startswith('--- Resumen [') or line.startswith('--- RECUERDO VIVIDO [') or line.startswith('# '):
                    summaries.append('\n'.join(current_summary))
                    current_tag = line.split('[')[0].strip(' -')
                    is_marker = line.startswith('--- Resumen [') or line.startswith('--- RECUERDO VIVIDO [')
                    current_summary = [line] if is_marker else []
                    in_summary = is_marker
                else:
                    current_summary.append(line)
        
        if current_summary:
            summaries.append('\n'.join(current_summary))
        
        return summaries
    
    def get_latest_memory(self, max_chars=1000):
        """Obtiene la memoria más reciente"""
        files = self.get_memory_files()
        
        if not files:
            return None
        
        last_file = files[-1]
        try:
            with open(last_file['filepath'], 'r', encoding='utf-8') as f:
                content = f.read()
                summaries = self.extract_summaries(content)
                
                if summaries:
                    latest = summaries[-1]
                    return latest[:max_chars] if len(latest) > max_chars else latest
        except Exception as e:
            print(f"Error leyendo memoria: {e}")
        
        return None
    
    def clear_all(self):
        """Elimina todos los archivos de memoria"""
        files = self.get_memory_files()
        for file_info in files:
            try:
                os.remove(file_info['filepath'])
            except Exception as e:
                print(f"Error eliminando {file_info['filename']}: {e}")
    
    def get_stats(self):
        """Obtiene estadísticas de la memoria"""
        files = self.get_memory_files()
        total_size = sum(f['size'] for f in files)
        
        return {
            'files': len(files),
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'memory_dir': self.memory_dir
        }

    def cleanup_memories(self, min_length=35):
        """
        Limpia memorias vacías o demasiado cortas (< min_length caracteres).
        Se ejecuta 'de vez en cuando' (por ejemplo, al inicio).
        """
        print(f"[DEBUG] Iniciando limpieza de memorias (min_len={min_length})...")
        files = self.get_memory_files()
        total_removed = 0
        
        for file_info in files:
            filepath = file_info['filepath']
            try:
                # Leer contenido completo
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Separar encabezado del contenido de memorias
                lines = content.split('\n')
                header_lines = []
                body_lines = []
                parsing_header = True
                
                for line in lines:
                    if parsing_header:
                        if line.startswith('--- Resumen [') or line.startswith('--- RECUERDO VIVIDO ['):
                            parsing_header = False
                            body_lines.append(line)
                        else:
                            header_lines.append(line)
                    else:
                        body_lines.append(line)
                
                # Si no hay cuerpo, es solo encabezado, verificar si vale la pena mantenerlo
                if not body_lines:
                    # Si el archivo está vacío (solo header), se podría borrar, pero mejor dejarlo
                    # para mantener la secuencia o borrarlo si se prefiere limpieza total
                    continue

                # Reconstruir body string
                body_content = '\n'.join(body_lines)
                
                # Extraer resúmenes usando la lógica existente
                summaries = self.extract_summaries(body_content)
                valid_summaries = []
                
                for summary in summaries:
                    # Limpiar encabezado del resumen para verificar longitud del CONTENIDO real
                    # El resumen tiene formato: "\n--- Resumen [FECHA] ---\nCONTENIDO..."
                    # Quitamos la primera línea (header del resumen) para validar longitud
                    parts = summary.strip().split('\n', 1)
                    if len(parts) > 1:
                        real_content = parts[1].strip()
                        if len(real_content) >= min_length:
                            valid_summaries.append(summary)
                        else:
                            print(f"[DEBUG] Eliminando memoria corta ({len(real_content)} chars) en {file_info['filename']}")
                            total_removed += 1
                    else:
                        # Caso raro: solo tiene header de resumen
                        print(f"[DEBUG] Eliminando memoria vacía en {file_info['filename']}")
                        total_removed += 1
                
                # Si hubo cambios, reescribir archivo
                if len(valid_summaries) != len(summaries):
                    print(f"[DEBUG] Reescribiendo {file_info['filename']} ({len(valid_summaries)} memorias válidas)")
                    
                    # Si no quedan memorias válidas, ¿borramos archivo o dejamos vacío?
                    # Dejemos el header + nada
                    new_content = '\n'.join(header_lines)
                    if valid_summaries:
                        new_content += '\n' + '\n'.join(valid_summaries) + '\n'
                        
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
            except Exception as e:
                print(f"[ERROR] Error limpiando {filepath}: {e}")
        
        if total_removed > 0:
            print(f"[DEBUG] Limpieza completada. Memorias eliminadas: {total_removed}")
        else:
            print("[DEBUG] Limpieza completada. No se encontraron memorias inválidas.")
