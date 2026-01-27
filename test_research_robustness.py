from web_researcher import WebResearcher
import time

def test_research():
    wr = WebResearcher()
    
    print("--- Test 1: Búsqueda Confiable (Quantum Computers) ---")
    start = time.time()
    results = wr.search("Quantum Computers", max_results=5, trusted_only=True)
    end = time.time()
    
    print(f"\nResultados encontrados: {len(results)}")
    print(f"Tiempo: {end - start:.2f}s")
    
    domains = set()
    for i, res in enumerate(results):
        print(f"[{i+1}] {res.get('title')} - {res.get('href')}")
        # Extract domain
        try:
            from urllib.parse import urlparse
            domain = urlparse(res.get('href')).netloc
            domains.add(domain)
        except: pass
        
    print(f"\nDominios únicos: {domains}")
    
    if len(results) > 0:
        print("✅ Búsqueda confiable exitosa.")
    else:
        print("❌ Búsqueda confiable fallida (sin resultados).")

    print("\n--- Test 2: Búsqueda Normal (Receta de paella) ---")
    results_normal = wr.search("Receta de paella valenciana", max_results=3, trusted_only=False)
    print(f"Resultados encontrados: {len(results_normal)}")
    for i, res in enumerate(results_normal):
        print(f"[{i+1}] {res.get('title')} - {res.get('href')}")

    if len(results_normal) > 0:
         print("✅ Búsqueda normal exitosa.")
    else:
         print("⚠️ Búsqueda normal sin resultados (puede ser error de red).")

if __name__ == "__main__":
    test_research()
