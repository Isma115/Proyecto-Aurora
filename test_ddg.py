from duckduckgo_search import DDGS
import sys

print(f"Python: {sys.version}")
try:
    with DDGS() as ddgs:
        print("DDGS initialized")
        results = list(ddgs.text("test", max_results=1))
        print(f"Results found: {len(results)}")
except Exception as e:
    print(f"ERROR: {e}")
