# -*- coding: utf-8 -*-
"""
Módulo de Investigación Web
Permite a Aurora buscar información en internet y aprender de ella.
"""

import os
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from datetime import datetime

class WebResearcher:
    """Clase encargada de buscar y procesar información de la web"""
    
    def __init__(self, knowledge_dir="conocimiento"):
        self.knowledge_dir = knowledge_dir
        if not os.path.exists(knowledge_dir):
            os.makedirs(knowledge_dir)
            
    def search(self, query, max_results=5, trusted_only=True):
        """Busca en DuckDuckGo y devuelve enlaces relevantes"""
        results = []
        seen_urls = set()
        
        try:
            with DDGS() as ddgs:
                if trusted_only:
                    print(f"[Research] Modo Estricto: Buscando '{query}' en fuentes confiables...")
                    
                    # Fuentes ampliadas y diversificadas
                    sources = [
                        "site:wikipedia.org",
                        "site:.edu", 
                        "site:.gov",
                        "site:.ac",   # Académico internacional
                        "site:.org",  # Organizaciones
                        "site:.es",
                        "site:britannica.com",
                        "site:sciencedirect.com",
                        "site:researchgate.net",
                        "site:nationalgeographic.com",
                        "site:bbc.com", # Noticias serias
                        "site:elpais.com",
                        "site:elmundo.es"
                    ]
                    
                    # 1. Wikipedia (Siempre intentamos obtener al menos 1)
                    try:
                        print(f"   > Consultando Wikipedia...")
                        gen = ddgs.text(f"{query} site:wikipedia.org", region='es-es', timelimit='y', max_results=2)
                        for r in gen:
                            if r['href'] not in seen_urls:
                                results.append(r)
                                seen_urls.add(r['href'])
                    except Exception as e:
                        print(f"   [WARN] Falló búsqueda en Wikipedia: {e}")

                    # 2. Búsqueda por fuentes confiables (iteramos para variedad)
                    # No paramos inmediatamente si llenamos, intentamos mezclar un poco.
                    for source in sources[1:]:
                        if len(results) >= max_results + 2: break # Buscamos un poco más para filtrar luego si hace falta
                        
                        try:
                            sq = f"{query} {source}"
                            # print(f"   > Consultando {source}...") # Reducir ruido
                            gen = ddgs.text(sq, region='es-es', timelimit='y', max_results=1)
                            for r in gen:
                                if r['href'] not in seen_urls:
                                    results.append(r)
                                    seen_urls.add(r['href'])
                        except Exception as e:
                            continue # Si falla una fuente, seguimos con la siguiente

                    # 3. Si tenemos muy pocos resultados, probamos .org general
                    if len(results) < 3:
                         try:
                            print("   > Buscando en dominios .org generales...")
                            gen = ddgs.text(f"{query} site:.org", region='es-es', timelimit='y', max_results=3)
                            for r in gen:
                                if r['href'] not in seen_urls:
                                    results.append(r)
                                    seen_urls.add(r['href'])
                         except Exception: pass

                else:
                    # Búsqueda normal más robusta
                    print(f"[Research] Buscando: {query}")
                    attempts = 0
                    while attempts < 3:
                        try:
                            gen = ddgs.text(query, region='es-es', timelimit='y', max_results=max_results)
                            for r in gen:
                                if r['href'] not in seen_urls:
                                    results.append(r)
                                    seen_urls.add(r['href'])
                            break # Éxito
                        except Exception as e:
                            attempts += 1
                            print(f"[Research] Reintentando búsqueda ({attempts}/3)... Error: {e}")
                            import time
                            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Error crítico en búsqueda DDGS: {e}")
            
        return results[:max_results] # Recortamos al final

    def scrape_url(self, url):
        """Descarga y extrae el texto principal de una URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Eliminar elementos no deseados
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
                
            # Extraer texto
            text = soup.get_text()
            
            # Limpiar líneas en blanco
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"[ERROR] Error scraping {url}: {e}")
            return None

    def deep_research(self, topic):
        """
        Realiza una investigación completa sobre un tema:
        1. Busca
        2. Lee los mejores resultados
        3. Guarda un resumen en la carpeta de conocimiento
        """
        print(f"--- Iniciando investigación profunda sobre: {topic} ---")
        
        # 1. Buscar
        results = self.search(f"{topic}", max_results=5, trusted_only=True) # Aumentamos resultados a 5
        if not results:
            print("[RESEARCH] Intento sin filtros estrictos...")
            # Fallback sin filtros si no encuentra nada
            results = self.search(f"{topic} información educativa", max_results=3, trusted_only=False)
            
        if not results:
            return False, "No se encontraron resultados fiables en la web."
            
        compiled_text = f"INVESTIGACIÓN SOBRE: {topic}\n"
        compiled_text += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        compiled_text += "=" * 50 + "\n\n"
        
        sources_count = 0
        
        # 2. Leer y compilar
        for res in results:
            title = res.get('title', 'Sin título')
            url = res.get('href', '')
            body = res.get('body', '')
            
            print(f"[RESEARCH] Procesando: {title}")
            
            # Intentar obtener contenido completo
            full_content = self.scrape_url(url)
            
            # Si falla el scrape, usamos el snippet de la búsqueda
            content_to_use = full_content if full_content and len(full_content) > 200 else body
            
            if content_to_use:
                compiled_text += f"FUENTE: {title}\nURL: {url}\n"
                compiled_text += "-" * 20 + "\n"
                # Limitar longitud por fuente para no saturar
                compiled_text += content_to_use[:3000] + "\n\n"
                compiled_text += "=" * 50 + "\n\n"
                sources_count += 1
        
        if sources_count == 0:
            return False, "No se pudo extraer información de las fuentes encontradas."
            
        # 3. Guardar
        filename = f"investigacion_{topic.replace(' ', '_').lower()}.txt"
        # Limpiar caracteres inválidos en nombre de archivo windows
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
            
        filepath = os.path.join(self.knowledge_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(compiled_text)
            return True, f"Investigación guardada en {filename} ({sources_count} fuentes)."
        except Exception as e:
            return False, f"Error guardando archivo: {e}"
