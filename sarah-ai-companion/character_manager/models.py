"""
Pydantic models for the Character Manager service
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CharacterCreateRequest(BaseModel):
    """Request model for character creation"""
    name: str = Field(..., description="Character name", min_length=1, max_length=255)
    user_id: str = Field(..., description="User ID who owns the character")
    persona_prompt: Optional[str] = Field(None, description="Full persona description")
    voice_id: Optional[str] = Field(None, description="ElevenLabs voice ID")
    appearance_seed: Optional[str] = Field(None, description="LoRA model ID for appearance")
    personality_traits: Optional[List[str]] = Field(None, description="List of personality traits")
    hobbies: Optional[List[str]] = Field(None, description="List of hobbies/interests")


class CharacterUpdateRequest(BaseModel):
    """Request model for character update"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    persona_prompt: Optional[str] = Field(None)
    voice_id: Optional[str] = Field(None)
    appearance_seed: Optional[str] = Field(None)


class CharacterResponse(BaseModel):
    """Response model for character data"""
    character_id: str = Field(..., description="Unique character identifier")
    user_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="Character name")
    persona_prompt: str = Field(..., description="Full persona description")
    voice_id: Optional[str] = Field(None, description="Voice ID for TTS")
    appearance_seed: Optional[str] = Field(None, description="LoRA model ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class CharacterListResponse(BaseModel):
    """Response model for character list"""
    characters: List[CharacterResponse] = Field(..., description="List of characters")
    total: int = Field(..., description="Total number of characters")


class PersonaGenerationRequest(BaseModel):
    """Request model for persona generation"""
    personality_traits: List[str] = Field(..., description="Personality traits", min_items=1)
    hobbies: List[str] = Field(default_factory=list, description="Hobbies and interests")
    background_hints: Optional[str] = Field(None, description="Additional background context")


class PersonaGenerationResponse(BaseModel):
    """Response model for persona generation"""
    persona_prompt: str = Field(..., description="Generated persona description")
    traits_used: List[str] = Field(..., description="Traits incorporated")
    hobbies_used: List[str] = Field(..., description="Hobbies incorporated")


class VoiceOption(BaseModel):
    """Model for available voice options"""
    voice_id: str = Field(..., description="ElevenLabs voice ID")
    name: str = Field(..., description="Voice name")
    description: str = Field(..., description="Voice description")
    preview_url: Optional[str] = Field(None, description="Preview audio URL")
    gender: Optional[str] = Field(None, description="Voice gender")
    age: Optional[str] = Field(None, description="Approximate age")


class AppearancePreset(BaseModel):
    """Model for appearance presets"""
    preset_id: str = Field(..., description="Preset identifier")
    name: str = Field(..., description="Preset name")
    description: str = Field(..., description="Appearance description")
    ethnicity: Optional[str] = Field(None)
    age_range: Optional[str] = Field(None)
    hair_color: Optional[str] = Field(None)
    eye_color: Optional[str] = Field(None)
    style_tags: List[str] = Field(default_factory=list)


class CharacterExportRequest(BaseModel):
    """Request model for character export"""
    character_id: str = Field(..., description="Character to export")
    include_memories: bool = Field(default=False, description="Include memory data")
    include_conversations: bool = Field(default=False, description="Include conversation history")


class CharacterExportResponse(BaseModel):
    """Response model for character export"""
    character_data: CharacterResponse = Field(..., description="Core character data")
    memories: Optional[List[dict]] = Field(None, description="Associated memories")
    conversations: Optional[List[dict]] = Field(None, description="Conversation history")
    export_version: str = Field(default="1.0", description="Export format version")
