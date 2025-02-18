import asyncio
from app.services.search.google_search import GoogleSearchClient
from app.services.search.search_manager import SearchManager

async def main():
    # Initialize GoogleSearchClient with API key and necessary configurations
    google_client = GoogleSearchClient()
    
    # Initialize SearchManager
    search_manager = SearchManager(google_client)

    # Perform a search query
    query = "What is ChatGPT?"
    results = await search_manager.search(query)

    # Print search results
    for idx, source in enumerate(results):
        print(f"{idx + 1}. {source.title} - {source.url} - {source.snippet}")

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
