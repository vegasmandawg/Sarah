"""
Sarah AI Companion - Multimodal Engine Service
Handles image generation with FLUX.1 and voice synthesis with ElevenLabs
"""

import asyncio
import logging
import os
import uuid
from typing import Dict, Optional, Any, List
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import httpx
import torch
from diffusers import FluxPipeline
from PIL import Image
import numpy as np
from io import BytesIO

from models import (
    ImageGenerationRequest, ImageGenerationResponse,
    VoiceGenerationRequest, VoiceGenerationResponse,
    LoRATrainingRequest, LoRATrainingResponse
)
from flux_manager import FluxManager
from lora_trainer import LoRATrainer
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model managers
flux_manager: Optional[FluxManager] = None
lora_trainer: Optional[LoRATrainer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global flux_manager, lora_trainer
    
    # Startup
    logger.info("Starting Multimodal Engine...")
    
    # Initialize FLUX model manager
    try:
        flux_manager = FluxManager(
            model_path=settings.FLUX_MODEL_PATH,
            device=settings.DEVICE,
            dtype=torch.float16 if settings.USE_FP16 else torch.float32
        )
        await flux_manager.initialize()
        logger.info("FLUX model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize FLUX model: {e}")
        flux_manager = None
    
    # Initialize LoRA trainer
    try:
        lora_trainer = LoRATrainer(
            base_model_path=settings.FLUX_MODEL_PATH,
            output_dir=settings.LORA_OUTPUT_DIR
        )
        logger.info("LoRA trainer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LoRA trainer: {e}")
        lora_trainer = None
    
    yield
    
    # Shutdown
    if flux_manager:
        flux_manager.cleanup()
    logger.info("Multimodal Engine shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Sarah Multimodal Engine",
    description="Image generation and voice synthesis service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def optimize_flux_prompt(user_prompt: str) -> str:
    """
    Use LLM to optimize prompt for FLUX.1 generation
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.PERSONA_ENGINE_URL}/api/chat",
                json={
                    "message": f"""You are a prompt engineer for FLUX.1 image generation. 
                    Convert this simple request into a detailed, optimized prompt: "{user_prompt}"
                    
                    Include:
                    - Detailed visual descriptions
                    - Artistic style (e.g., photorealistic, cinematic lighting)
                    - Composition details
                    - Quality markers (8k, highly detailed, professional)
                    
                    Keep it under 200 words and don't include negative prompts.""",
                    "character_id": "system",
                    "user_id": "system"
                }
            )
            
            if response.status_code == 200:
                optimized = response.json().get("response", user_prompt)
                logger.info(f"Optimized prompt: {optimized[:100]}...")
                return optimized
            else:
                logger.error(f"Failed to optimize prompt: {response.status_code}")
                return user_prompt
                
    except Exception as e:
        logger.error(f"Error optimizing prompt: {e}")
        return user_prompt


async def add_emotion_to_text(text: str) -> str:
    """
    Use LLM to add emotional cues to text for TTS
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.PERSONA_ENGINE_URL}/api/chat",
                json={
                    "message": f"""Add subtle emotional cues to this text for text-to-speech: "{text}"
                    
                    Use markers like [excitedly], [softly], [thoughtfully] sparingly and only where it enhances the delivery.
                    Return only the modified text, nothing else.""",
                    "character_id": "system",
                    "user_id": "system"
                }
            )
            
            if response.status_code == 200:
                enhanced = response.json().get("response", text)
                logger.info(f"Enhanced text for TTS: {enhanced[:100]}...")
                return enhanced
            else:
                logger.error(f"Failed to enhance text: {response.status_code}")
                return text
                
    except Exception as e:
        logger.error(f"Error enhancing text: {e}")
        return text


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "flux_model": "loaded" if flux_manager and flux_manager.is_ready else "not_loaded",
            "lora_trainer": "available" if lora_trainer else "unavailable",
            "gpu_available": torch.cuda.is_available()
        },
        "gpu_info": {
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None
        }
    }


@app.post("/generate/image", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest, background_tasks: BackgroundTasks):
    """Generate an image using FLUX.1"""
    if not flux_manager or not flux_manager.is_ready:
        raise HTTPException(status_code=503, detail="FLUX model not available")
    
    try:
        # Generate unique filename
        image_id = str(uuid.uuid4())
        filename = f"{image_id}.png"
        filepath = os.path.join(settings.OUTPUT_DIR, filename)
        
        # Optimize prompt using LLM
        optimized_prompt = await optimize_flux_prompt(request.prompt)
        
        # Add LoRA trigger word if character LoRA specified
        if request.character_lora_id:
            # In production, fetch trigger word from database
            trigger_word = "sarah"  # Placeholder
            optimized_prompt = f"{trigger_word}, {optimized_prompt}"
        
        # Add negative prompt
        negative_prompt = request.negative_prompt or settings.DEFAULT_NEGATIVE_PROMPT
        
        # Generate image
        logger.info(f"Generating image with prompt: {optimized_prompt[:100]}...")
        
        image = await flux_manager.generate(
            prompt=optimized_prompt,
            negative_prompt=negative_prompt,
            lora_path=request.character_lora_id,
            num_inference_steps=request.num_inference_steps or settings.DEFAULT_INFERENCE_STEPS,
            guidance_scale=request.guidance_scale or settings.DEFAULT_GUIDANCE_SCALE,
            width=request.width or 1024,
            height=request.height or 1024,
            seed=request.seed
        )
        
        # Save image
        image.save(filepath, "PNG")
        logger.info(f"Image saved to {filepath}")
        
        # Schedule cleanup after delay
        if settings.AUTO_CLEANUP:
            background_tasks.add_task(cleanup_file, filepath, settings.CLEANUP_DELAY)
        
        return ImageGenerationResponse(
            image_id=image_id,
            filename=filename,
            prompt=optimized_prompt,
            width=image.width,
            height=image.height,
            url=f"/outputs/{filename}"
        )
        
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/voice", response_model=VoiceGenerationResponse)
async def generate_voice(request: VoiceGenerationRequest, background_tasks: BackgroundTasks):
    """Generate voice audio using ElevenLabs API"""
    try:
        # Add emotional cues to text
        enhanced_text = await add_emotion_to_text(request.text)
        
        # Generate unique filename
        audio_id = str(uuid.uuid4())
        filename = f"{audio_id}.mp3"
        filepath = os.path.join(settings.OUTPUT_DIR, filename)
        
        # Call ElevenLabs API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ELEVENLABS_API_URL}/text-to-speech/{request.voice_id or settings.DEFAULT_VOICE_ID}",
                headers={
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": settings.ELEVENLABS_API_KEY
                },
                json={
                    "text": enhanced_text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": request.stability or 0.5,
                        "similarity_boost": request.similarity_boost or 0.5
                    }
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"ElevenLabs API error: {response.text}"
                )
            
            # Save audio file
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Voice audio saved to {filepath}")
            
            # Schedule cleanup
            if settings.AUTO_CLEANUP:
                background_tasks.add_task(cleanup_file, filepath, settings.CLEANUP_DELAY)
            
            return VoiceGenerationResponse(
                audio_id=audio_id,
                filename=filename,
                text=request.text,
                enhanced_text=enhanced_text,
                voice_id=request.voice_id or settings.DEFAULT_VOICE_ID,
                url=f"/outputs/{filename}"
            )
            
    except httpx.RequestError as e:
        logger.error(f"Voice generation request failed: {e}")
        raise HTTPException(status_code=503, detail="Voice generation service unavailable")
    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train-lora", response_model=LoRATrainingResponse)
async def train_lora(
    character_id: str = Form(...),
    images: List[UploadFile] = File(...),
    trigger_word: str = Form(default="sarah"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Train a LoRA for character consistency (internal endpoint)"""
    if not lora_trainer:
        raise HTTPException(status_code=503, detail="LoRA trainer not available")
    
    try:
        # Validate images
        if len(images) < settings.MIN_LORA_IMAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum {settings.MIN_LORA_IMAGES} images required for LoRA training"
            )
        
        # Create training directory
        training_id = f"{character_id}_{uuid.uuid4().hex[:8]}"
        training_dir = os.path.join(settings.TEMP_DIR, training_id)
        os.makedirs(training_dir, exist_ok=True)
        
        # Save uploaded images
        image_paths = []
        for idx, image in enumerate(images):
            image_path = os.path.join(training_dir, f"image_{idx}.png")
            contents = await image.read()
            
            # Validate and save image
            try:
                img = Image.open(BytesIO(contents))
                img.save(image_path, "PNG")
                image_paths.append(image_path)
            except Exception as e:
                logger.error(f"Invalid image file: {e}")
                continue
        
        if not image_paths:
            raise HTTPException(status_code=400, detail="No valid images provided")
        
        # Start training in background
        lora_path = os.path.join(settings.LORA_OUTPUT_DIR, f"{training_id}.safetensors")
        
        background_tasks.add_task(
            lora_trainer.train,
            image_paths=image_paths,
            output_path=lora_path,
            trigger_word=trigger_word,
            character_id=character_id
        )
        
        return LoRATrainingResponse(
            training_id=training_id,
            status="training_started",
            character_id=character_id,
            trigger_word=trigger_word,
            estimated_time_minutes=15
        )
        
    except Exception as e:
        logger.error(f"LoRA training initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/outputs/{filename}")
async def get_output_file(filename: str):
    """Serve generated files"""
    filepath = os.path.join(settings.OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    if filename.endswith(".png"):
        media_type = "image/png"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        media_type = "image/jpeg"
    elif filename.endswith(".mp3"):
        media_type = "audio/mpeg"
    elif filename.endswith(".wav"):
        media_type = "audio/wav"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(filepath, media_type=media_type)


async def cleanup_file(filepath: str, delay: int):
    """Clean up generated files after delay"""
    await asyncio.sleep(delay)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Cleaned up file: {filepath}")
    except Exception as e:
        logger.error(f"Failed to clean up file {filepath}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
