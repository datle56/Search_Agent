import asyncio
from app.services.llm.openai_client import OpenAIChatClient

async def main():
    # Initialize OpenAI client with the specified model
    chat_client = OpenAIChatClient(model="gpt-4o-mini")

    # Sample user message
    messages = [{"role": "user", "content": "Hello! What can you do?"}]

    # Send a real request to OpenAI API
    response = await chat_client.chat_completion(messages=messages)

    # Print the assistant's response
    print("Assistant:", response.choices[0].message.content)

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
