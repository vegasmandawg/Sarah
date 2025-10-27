"""
Pydantic models for the Persona Engine service
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message", min_length=1)
    character_id: str = Field(default="default", description="Character ID to use")
    user_id: str = Field(..., description="User ID")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for context")
    stream: bool = Field(default=True, description="Whether to stream the response")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="AI response")
    character_id: str = Field(..., description="Character ID used")
    sentiment: Optional[Dict[str, float]] = Field(default=None, description="Sentiment analysis of user message")
    generation_params: Optional[Dict[str, float]] = Field(default=None, description="Generation parameters used")


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis"""
    text: str = Field(..., description="Text to analyze", min_length=1)


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis"""
    compound: float = Field(..., description="Compound sentiment score (-1 to 1)")
    positive: float = Field(..., description="Positive sentiment score (0 to 1)")
    negative: float = Field(..., description="Negative sentiment score (0 to 1)")
    neutral: float = Field(..., description="Neutral sentiment score (0 to 1)")


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str = Field(..., description="Message type: 'message', 'status', 'token', 'complete', 'error'")
    content: Optional[str] = Field(default=None, description="Message content")
    task: Optional[str] = Field(default=None, description="Current task for status messages")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CharacterContext(BaseModel):
    """Character context from Character Manager"""
    character_id: str = Field(..., description="Character ID")
    name: str = Field(..., description="Character name")
    persona_prompt: str = Field(..., description="Character persona definition")
    voice_id: Optional[str] = Field(default=None, description="Voice ID for TTS")
    appearance_seed: Optional[str] = Field(default=None, description="Appearance seed/LoRA ID")


class MemoryContext(BaseModel):
    """Memory context from Memory Subsystem"""
    context: str = Field(..., description="Formatted memory context")
    relevant_facts: List[Dict[str, Any]] = Field(default_factory=list, description="Relevant structured facts")
    conversation_snippets: List[str] = Field(default_factory=list, description="Relevant conversation snippets")
