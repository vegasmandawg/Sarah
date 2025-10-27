"""
Pydantic models for the Multimodal Engine service
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., description="Text prompt for image generation", min_length=1)
    negative_prompt: Optional[str] = Field(default=None, description="Negative prompt to avoid certain features")
    character_lora_id: Optional[str] = Field(default=None, description="LoRA model ID for character consistency")
    width: Optional[int] = Field(default=1024, ge=256, le=2048, description="Image width")
    height: Optional[int] = Field(default=1024, ge=256, le=2048, description="Image height")
    num_inference_steps: Optional[int] = Field(default=30, ge=10, le=100, description="Number of denoising steps")
    guidance_scale: Optional[float] = Field(default=7.5, ge=1.0, le=20.0, description="Guidance scale for generation")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")
    aspect_ratio: Optional[str] = Field(default="1:1", description="Aspect ratio preset")


class ImageGenerationResponse(BaseModel):
    """Response model for image generation"""
    image_id: str = Field(..., description="Unique identifier for the generated image")
    filename: str = Field(..., description="Filename of the generated image")
    prompt: str = Field(..., description="Optimized prompt used for generation")
    width: int = Field(..., description="Actual width of generated image")
    height: int = Field(..., description="Actual height of generated image")
    url: str = Field(..., description="URL to access the generated image")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VoiceGenerationRequest(BaseModel):
    """Request model for voice generation"""
    text: str = Field(..., description="Text to convert to speech", min_length=1, max_length=5000)
    voice_id: Optional[str] = Field(default=None, description="ElevenLabs voice ID")
    stability: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Voice stability")
    similarity_boost: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Voice similarity boost")
    style: Optional[float] = Field(default=0.0, ge=0.0, le=1.0, description="Style exaggeration")


class VoiceGenerationResponse(BaseModel):
    """Response model for voice generation"""
    audio_id: str = Field(..., description="Unique identifier for the generated audio")
    filename: str = Field(..., description="Filename of the generated audio")
    text: str = Field(..., description="Original text")
    enhanced_text: str = Field(..., description="Text with emotional cues added")
    voice_id: str = Field(..., description="Voice ID used for generation")
    url: str = Field(..., description="URL to access the generated audio")
    duration_seconds: Optional[float] = Field(default=None, description="Duration of audio in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LoRATrainingRequest(BaseModel):
    """Request model for LoRA training"""
    character_id: str = Field(..., description="Character ID for the LoRA")
    trigger_word: str = Field(default="sarah", description="Trigger word for the LoRA")
    num_images: int = Field(..., ge=5, le=50, description="Number of training images")
    training_steps: Optional[int] = Field(default=1000, ge=100, le=5000, description="Number of training steps")
    learning_rate: Optional[float] = Field(default=1e-4, description="Learning rate for training")


class LoRATrainingResponse(BaseModel):
    """Response model for LoRA training"""
    training_id: str = Field(..., description="Unique identifier for the training job")
    status: str = Field(..., description="Training status")
    character_id: str = Field(..., description="Associated character ID")
    trigger_word: str = Field(..., description="Trigger word for the trained LoRA")
    estimated_time_minutes: int = Field(..., description="Estimated training time in minutes")
    lora_path: Optional[str] = Field(default=None, description="Path to trained LoRA model")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LoRATrainingStatus(BaseModel):
    """Status update for LoRA training"""
    training_id: str = Field(..., description="Training job ID")
    status: str = Field(..., description="Current status: pending, training, completed, failed")
    progress: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Training progress percentage")
    current_step: Optional[int] = Field(default=None, description="Current training step")
    total_steps: Optional[int] = Field(default=None, description="Total training steps")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


class GenerationMetrics(BaseModel):
    """Metrics for generation operations"""
    operation_type: str = Field(..., description="Type of operation: image or voice")
    processing_time_seconds: float = Field(..., description="Time taken for generation")
    model_load_time_seconds: Optional[float] = Field(default=None, description="Time to load model")
    inference_time_seconds: Optional[float] = Field(default=None, description="Pure inference time")
    post_processing_time_seconds: Optional[float] = Field(default=None, description="Post-processing time")
