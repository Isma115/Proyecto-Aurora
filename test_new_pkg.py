try:
    from ddgs import DDGS
    print("Imported DDGS from ddgs package")
except ImportError:
    print("Could not import DDGS from ddgs")
    try:
        from duckduckgo_search import DDGS
        print("Imported DDGS from duckduckgo_search (fallback)")
    except ImportError:
        print("Failed to import DDGS")
        exit(1)

import sys
print(f"Python: {sys.version}")

try:
    with DDGS() as ddgs:
        print("DDGS initialized")
        # Test basic search
        results = list(ddgs.text("python programming", max_results=3))
        print(f"Results found: {len(results)}")
        for r in results:
            print(f"- {r.get('title')}: {r.get('href')}")
            
except Exception as e:
    print(f"ERROR: {e}")
