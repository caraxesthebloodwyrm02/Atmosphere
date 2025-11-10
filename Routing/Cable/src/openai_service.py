"""
Secure OpenAI Service Integration
Handles all interactions with OpenAI's API
"""
import os
from typing import Dict, Any, Optional, List
import openai
from dotenv import load_dotenv
import logging
import httpx

# Set up logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class OpenAIService:
    """Handles all OpenAI API interactions"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        logger.info("OpenAI client initialized successfully")
    
    async def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Get embedding for a single text"""
        try:
            # Make a synchronous call to the OpenAI API
            response = self.client.embeddings.create(
                input=text,
                model=model
            )
            # Return the embedding list
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            raise
    
    async def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Get chat completion from OpenAI"""
        try:
            # Make a synchronous call to the OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise
    
    async def transcribe_audio(
        self,
        audio_file_path: str,
        model: str = "whisper-1",
        response_format: str = "text"
    ) -> str:
        """Transcribe audio using Whisper"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    response_format=response_format
                )
            return response
        except Exception as e:
            logger.error(f"Error in audio transcription: {str(e)}")
            raise

    async def direct_call(self, method: str, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Makes a direct, authenticated HTTP call to any OpenAI API endpoint path."""
        base_url = "https://api.openai.com"
        url = f"{base_url}{path}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error in direct call to '{path}': {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error in direct call to '{path}': {str(e)}")
            raise

# Singleton instance
openai_service = OpenAIService()
