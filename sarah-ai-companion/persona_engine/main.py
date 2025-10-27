"""
Sarah AI Companion - Persona Engine Service
Main FastAPI application for conversational AI with Ollama integration
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import redis.asyncio as redis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from prompt_manager import PromptManager
from models import ChatMessage, ChatRequest, SentimentRequest, SentimentResponse
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

# Global Redis client
redis_client: Optional[redis.Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global redis_client
    
    # Startup
    logger.info("Starting Persona Engine...")
    
    # Initialize Redis connection
    try:
        redis_client = await redis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None
    
    # Initialize prompt manager
    app.state.prompt_manager = PromptManager()
    
    # Verify Ollama connection
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                logger.info("Connected to Ollama")
            else:
                logger.warning("Ollama connection test failed")
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()
    logger.info("Persona Engine shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Sarah Persona Engine",
    description="Conversational AI service with dynamic persona management",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)


# Initialize connection manager
manager = ConnectionManager()


async def analyze_sentiment(text: str) -> Dict[str, float]:
    """Analyze sentiment using VADER"""
    scores = sentiment_analyzer.polarity_scores(text)
    return {
        "compound": scores["compound"],
        "positive": scores["pos"],
        "negative": scores["neg"],
        "neutral": scores["neu"]
    }


def adjust_generation_params(sentiment_score: float) -> Dict[str, float]:
    """Adjust LLM generation parameters based on sentiment"""
    # Base parameters
    base_temp = 0.7
    base_top_p = 0.9
    
    # Adjust based on sentiment
    if sentiment_score > 0.5:  # Positive sentiment
        # More creative and playful
        temperature = min(base_temp + 0.2, 1.0)
        top_p = min(base_top_p + 0.05, 1.0)
    elif sentiment_score < -0.3:  # Negative sentiment
        # More focused and serious
        temperature = max(base_temp - 0.2, 0.3)
        top_p = max(base_top_p - 0.1, 0.7)
    else:  # Neutral sentiment
        temperature = base_temp
        top_p = base_top_p
    
    return {
        "temperature": temperature,
        "top_p": top_p
    }


async def fetch_character_context(character_id: str, user_id: str) -> Dict[str, Any]:
    """Fetch character information from Character Manager service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://character_manager:8000/characters/{character_id}",
                headers={"X-User-ID": user_id}
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch character: {response.status_code}")
                return {}
    except Exception as e:
        logger.error(f"Error fetching character context: {e}")
        return {}


async def fetch_memory_context(user_message: str, character_id: str, user_id: str) -> str:
    """Fetch relevant memory context from Memory Subsystem"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://memory_subsystem:8000/retrieve-context",
                json={
                    "message": user_message,
                    "character_id": character_id,
                    "user_id": user_id
                }
            )
            if response.status_code == 200:
                return response.json().get("context", "")
            else:
                logger.error(f"Failed to fetch memory context: {response.status_code}")
                return ""
    except Exception as e:
        logger.error(f"Error fetching memory context: {e}")
        return ""


async def stream_ollama_response(
    prompt: str,
    generation_params: Dict[str, float],
    websocket: WebSocket
) -> str:
    """Stream response from Ollama API"""
    full_response = ""
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Prepare the request
            request_data = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": generation_params["temperature"],
                    "top_p": generation_params["top_p"],
                    "num_predict": 2048
                }
            }
            
            # Stream the response
            async with client.stream(
                "POST",
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=request_data
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                token = chunk["response"]
                                full_response += token
                                
                                # Send token to client
                                await websocket.send_json({
                                    "type": "token",
                                    "content": token
                                })
                                
                            if chunk.get("done", False):
                                break
                                
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse Ollama response: {line}")
                            
    except Exception as e:
        logger.error(f"Error streaming from Ollama: {e}")
        await websocket.send_json({
            "type": "error",
            "content": "Failed to generate response"
        })
    
    return full_response


async def publish_conversation_turn(
    user_id: str,
    character_id: str,
    user_message: str,
    ai_response: str
):
    """Publish conversation turn to Redis for memory processing"""
    if not redis_client:
        logger.warning("Redis not available, skipping conversation publish")
        return
    
    try:
        conversation_data = {
            "user_id": user_id,
            "character_id": character_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await redis_client.publish(
            "conversation_turns",
            json.dumps(conversation_data)
        )
        logger.info("Published conversation turn to Redis")
        
    except Exception as e:
        logger.error(f"Failed to publish conversation turn: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check Ollama connection
    ollama_healthy = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            ollama_healthy = response.status_code == 200
    except:
        pass
    
    # Check Redis connection
    redis_healthy = False
    if redis_client:
        try:
            await redis_client.ping()
            redis_healthy = True
        except:
            pass
    
    return {
        "status": "healthy" if ollama_healthy else "degraded",
        "services": {
            "ollama": "connected" if ollama_healthy else "disconnected",
            "redis": "connected" if redis_healthy else "disconnected"
        }
    }


@app.post("/api/sentiment", response_model=SentimentResponse)
async def analyze_text_sentiment(request: SentimentRequest):
    """Analyze sentiment of provided text"""
    scores = await analyze_sentiment(request.text)
    return SentimentResponse(**scores)


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat"""
    client_id = f"client_{id(websocket)}"
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            user_message = data.get("message", "")
            character_id = data.get("character_id", "default")
            user_id = data.get("user_id", "anonymous")
            
            if not user_message:
                await websocket.send_json({
                    "type": "error",
                    "content": "Empty message received"
                })
                continue
            
            # Send status update
            await websocket.send_json({
                "type": "status",
                "task": "processing_message"
            })
            
            # Analyze sentiment
            sentiment_scores = await analyze_sentiment(user_message)
            sentiment_compound = sentiment_scores["compound"]
            
            # Adjust generation parameters based on sentiment
            generation_params = adjust_generation_params(sentiment_compound)
            
            # Fetch character context
            character_data = await fetch_character_context(character_id, user_id)
            persona_definition = character_data.get("persona_prompt", "")
            
            # Fetch memory context
            memory_context = await fetch_memory_context(user_message, character_id, user_id)
            
            # Construct dynamic prompt
            prompt_manager: PromptManager = app.state.prompt_manager
            full_prompt = prompt_manager.construct_prompt(
                user_message=user_message,
                persona_definition=persona_definition,
                memory_context=memory_context
            )
            
            # Send status update
            await websocket.send_json({
                "type": "status",
                "task": "generating_response"
            })
            
            # Stream response from Ollama
            ai_response = await stream_ollama_response(
                prompt=full_prompt,
                generation_params=generation_params,
                websocket=websocket
            )
            
            # Send completion signal
            await websocket.send_json({
                "type": "complete",
                "sentiment": sentiment_scores
            })
            
            # Publish conversation turn for memory processing
            await publish_conversation_turn(
                user_id=user_id,
                character_id=character_id,
                user_message=user_message,
                ai_response=ai_response
            )
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
