"""
Pydantic models for the Memory Subsystem service
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class FactType(str, Enum):
    """Types of facts that can be stored"""
    PREFERENCE = "preference"
    EVENT = "event"
    RELATIONSHIP = "relationship"
    PERSONAL_INFO = "personal_info"
    GOAL = "goal"
    HABIT = "habit"
    OTHER = "other"


class MemoryRetrievalRequest(BaseModel):
    """Request model for memory retrieval"""
    message: str = Field(..., description="Current user message to find context for")
    user_id: str = Field(..., description="User ID")
    character_id: str = Field(..., description="Character ID")
    max_facts: Optional[int] = Field(default=10, ge=1, le=50, description="Maximum number of facts to retrieve")
    max_snippets: Optional[int] = Field(default=5, ge=1, le=20, description="Maximum number of conversation snippets")


class MemoryRetrievalResponse(BaseModel):
    """Response model for memory retrieval"""
    context: str = Field(..., description="Formatted context string ready for LLM injection")
    relevant_facts: List[Dict[str, Any]] = Field(default_factory=list, description="List of relevant facts")
    conversation_snippets: List[str] = Field(default_factory=list, description="List of relevant conversation snippets")


class ConversationTurn(BaseModel):
    """Model for a conversation turn"""
    user_id: str = Field(..., description="User ID")
    character_id: str = Field(..., description="Character ID")
    user_message: str = Field(..., description="User's message")
    ai_response: str = Field(..., description="AI's response")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = Field(default=None, description="Conversation session ID")


class KeyFact(BaseModel):
    """Model for a key fact"""
    user_id: str = Field(..., description="User ID")
    character_id: str = Field(..., description="Character ID")
    fact_type: FactType = Field(..., description="Type of fact")
    fact_key: str = Field(..., description="Fact identifier/key", max_length=255)
    fact_value: str = Field(..., description="Fact value/content")
    confidence: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")


class MemoryExtractionRequest(BaseModel):
    """Request model for memory extraction from conversation"""
    user_message: str = Field(..., description="User's message")
    ai_response: str = Field(..., description="AI's response")
    user_id: str = Field(..., description="User ID")
    character_id: str = Field(..., description="Character ID")


class MemoryExtractionResponse(BaseModel):
    """Response model for memory extraction"""
    facts: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted facts")
    entities: List[Dict[str, str]] = Field(default_factory=list, description="Extracted entities")
    topics: List[str] = Field(default_factory=list, description="Conversation topics")
    sentiment: Optional[str] = Field(default=None, description="Overall sentiment")


class MemorySearchRequest(BaseModel):
    """Request model for memory search"""
    query: str = Field(..., description="Search query")
    user_id: str = Field(..., description="User ID")
    character_id: Optional[str] = Field(default=None, description="Character ID (optional)")
    search_facts: bool = Field(default=True, description="Search in key facts")
    search_conversations: bool = Field(default=True, description="Search in conversations")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")


class MemorySearchResponse(BaseModel):
    """Response model for memory search"""
    facts: List[Dict[str, Any]] = Field(default_factory=list, description="Matching facts")
    conversations: List[Dict[str, Any]] = Field(default_factory=list, description="Matching conversations")
    total_results: int = Field(..., description="Total number of results found")


class MemoryStats(BaseModel):
    """Memory statistics for a user/character"""
    user_id: str = Field(..., description="User ID")
    character_id: str = Field(..., description="Character ID")
    total_facts: int = Field(..., description="Total number of stored facts")
    fact_breakdown: Dict[str, int] = Field(..., description="Facts by type")
    total_conversations: int = Field(..., description="Total conversation snippets")
    oldest_memory: Optional[datetime] = Field(default=None, description="Oldest memory timestamp")
    newest_memory: Optional[datetime] = Field(default=None, description="Newest memory timestamp")
    storage_size_mb: float = Field(..., description="Approximate storage size in MB")
