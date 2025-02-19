from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from typing import AsyncGenerator
from datetime import datetime

# Import the SearchAgent and related clients for research functionality
from app.core.agent import SearchAgent
from app.services.llm.openai_client import OpenAIChatClient
from app.services.search.search_manager import SearchManager
from app.services.search.google_search import GoogleSearchClient

# Initialize the FastAPI application
app = FastAPI()

# Add Cross-Origin Resource Sharing (CORS) middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (modify this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a Pydantic model for the research request payload
class ResearchRequest(BaseModel):
    concept: str          # The concept to research
    stream: bool = True   # Flag to enable or disable streaming response

# Custom JSON encoder to handle datetime objects when serializing data
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO formatted string
        return super().default(obj)

# Asynchronous generator to yield Server-Sent Event (SSE) messages from a queue
async def event_generator(queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    while True:
        try:
            # Wait for new data from the queue
            data = await queue.get()
            # When data is None and queue is empty, it signals the end of the stream
            if data is None and queue.empty():
                break
            # Yield the event message using the custom JSON encoder
            yield f"data: {json.dumps(data, cls=CustomJSONEncoder)}\n\n"
        except Exception as e:
            # If an error occurs, yield an error event and break the loop
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
            break

# Define the research endpoint that handles both streaming and non-streaming responses
@app.post("/research")
async def research_concept(request: ResearchRequest):
    # Instantiate the OpenAI chat client and search manager with a Google search client
    chat_client = OpenAIChatClient(model='gpt-4o-mini')
    search_manager = SearchManager(
        google_client=GoogleSearchClient(),
    )

    # If the client does not want a streaming response, execute synchronously
    if not request.stream:
        try:
            agent = SearchAgent(
                chat_client=chat_client,
                search_manager=search_manager,
                min_nodes=3,
                max_nodes=5,
            )
            # Execute the research process and dump the resulting graph
            graph = await agent.research_concept(request.concept)
            return graph.model_dump()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # For streaming response, create an asynchronous queue to send events
    queue = asyncio.Queue()
    
    # Send an initial event indicating the start of the research process
    await queue.put({
        "type": "start",
        "data": {"message": "Starting research..."}
    })
    
    # Define an update handler to push updates into the queue
    def update_handler(data: dict):
        # Schedule the queue update as a background task
        asyncio.create_task(queue.put(data))
    
    # Define the asynchronous research runner that will update the queue with progress
    async def run_research():
        try:
            agent = SearchAgent(
                chat_client=chat_client,
                search_manager=search_manager,
                min_nodes=3,
                max_nodes=5,
                on_update=update_handler  # Pass the update handler to the agent
            )
            # Run the research process asynchronously
            await agent.research_concept(request.concept)
            # Once research is complete, push a None value to signal the end of the stream
            await queue.put(None)
        except Exception as e:
            # On error, send an error event and then signal completion
            await queue.put({
                "type": "error",
                "data": str(e)
            })
            await queue.put(None)
    
    # Start the research process in the background
    asyncio.create_task(run_research())
    
    # Return a StreamingResponse that uses the event generator to stream updates to the client
    return StreamingResponse(
        event_generator(queue),
        media_type="text/event-stream"
    )

# Health check endpoints
@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
