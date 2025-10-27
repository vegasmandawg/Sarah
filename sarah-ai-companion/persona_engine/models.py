"""
Pydantic models for the Persona Engine service
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatPreferences(BaseModel):
    """Optional chat preference payload for adult tuning"""

    mood: Optional[str] = Field(default=None, description="Overall mood or tone to adopt")
    explicit_level: Optional[str] = Field(default=None, description="How explicit the response should be")
    intensity: Optional[int] = Field(default=None, ge=0, le=100, description="Heat/intensity slider (0-100)")
    pacing: Optional[str] = Field(default=None, description="Conversation pacing preference")
    narration_style: Optional[str] = Field(default=None, description="Narration perspective preference")
    roleplay_mode: Optional[bool] = Field(default=None, description="Whether to remain fully in character")
    allow_narration: Optional[bool] = Field(default=None, description="Whether to describe sensations narratively")
    safe_word: Optional[str] = Field(default=None, description="Active safe word to respect")
    green_lights: List[str] = Field(default_factory=list, description="Allowed turn-ons or focus areas")
    hard_limits: List[str] = Field(default_factory=list, description="Topics or actions that must be avoided")
    aftercare_notes: Optional[str] = Field(default=None, description="How to deliver aftercare once scene winds down")


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
    preferences: Optional[ChatPreferences] = Field(default=None, description="User's intimacy configuration")


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
