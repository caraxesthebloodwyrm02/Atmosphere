import asyncio
import json
from dotenv import load_dotenv

# Add src to path to allow importing openai_service
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from openai_service import openai_service

async def main():
    """
    Demonstrates a platform-level call to the OpenAI API using the direct_call method.
    """
    print("--- Preparing Direct Platform-Level Call to OpenAI ---")

    # The specific API path we want to hit
    path = "/v1/chat/completions"

    # The payload for the request
    payload = {
        "model": "gpt-4-turbo-preview",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Confirm you received this direct platform call."
            }
        ],
        "temperature": 0.7
    }

    print(f"Target Path: {path}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-----------------------------------------------------")

    try:
        # Use the direct_call method from the platform's service layer
        response_json = await openai_service.direct_call(
            method="POST",
            path=path,
            payload=payload
        )

        print("--- Received Response from OpenAI ---")
        print("Response JSON:")
        print(json.dumps(response_json, indent=2))
        print("-------------------------------------")
        print("\n✅ Platform-level call successful.")

    except Exception as e:
        print(f"\n--- An Error Occurred ---")
        print(f"Failed to make direct call: {str(e)}")
        print("-------------------------")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
