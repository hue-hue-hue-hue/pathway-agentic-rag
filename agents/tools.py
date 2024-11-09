from duckduckgo_search import DDGS
from tavily import TavilyClient
from datetime import datetime
from typing import List, Dict, Any
import os


class SearchTools:
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_KEY"))
        self.current_date = datetime.now().strftime("%Y-%m")

    def advanced_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Advanced search using Tavily API for comprehensive results
        """
        print(f"Running advanced search for: {query}...")
        try:
            results = self.tavily_client.search(query)
            return results
        except Exception as e:
            print(f"Tavily search failed: {str(e)}")
            return []

    def quick_search(self, query: str, max_results: int = 5) -> str:
        """
        Quick search using DuckDuckGo for faster, simpler results
        """
        print(f"Running quick search for: {query}...")
        try:
            ddg_api = DDGS()
            results = ddg_api.text(
                f"{query} {self.current_date}", max_results=max_results
            )

            if results:
                search_results = "\n\n".join(
                    [
                        f"Title: {result['title']}\n"
                        f"URL: {result['href']}\n"
                        f"Description: {result['body']}"
                        for result in results
                    ]
                )
                return search_results
            return f"No results found for: {query}"

        except Exception as e:
            print(f"DuckDuckGo search failed: {str(e)}")
            return f"Search failed: {str(e)}"
