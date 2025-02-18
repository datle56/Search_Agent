from typing import List
import asyncio
from app.services.search.google_search import GoogleSearchClient
from app.services.search.base import Source

class SearchManager:
    def __init__(self, google_client: GoogleSearchClient):
        self.google_client = google_client

    async def search(self, query: str, google_results: int = 5) -> List[Source]:
        """
        Perform a search using only Google

        Args:
            query: Search query string
            google_results: Number of Google results to retrieve
        """
        # Run Google search
        google_task = self.google_client.search(query, google_results)
        results = await asyncio.gather(google_task)
        
        all_sources = []
        seen_urls = set()

        for source_list in results:
            for source in source_list:
                if source.url not in seen_urls:
                    seen_urls.add(source.url)
                    all_sources.append(source)

        return all_sources