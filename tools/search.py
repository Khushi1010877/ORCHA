#Query → DuckDuckGo → Raw Results → Clean JSON → Return list
#WebSearchTool → runs DuckDuckGo searches
#executor.py depends on it to fetch real results

from ddgs import DDGS

class WebSearchTool:
    def query(self, query: str, source: str = "duckduckgo") -> list:
        try:
            with DDGS() as ddgs:
                raw_results = ddgs.text(query, max_results=20)
                results = list(raw_results) if raw_results is not None else []
                return [
                    {
                        "text": item.get("body", ""),
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "source": source,
                        "query": query,
                    }
                    for item in results
                    if isinstance(item, dict)
                ]
        except Exception as e:
            print(f"[Search] Error for '{query}': {e}")
            return []