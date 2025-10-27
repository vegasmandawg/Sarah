"""
FLUX Model Manager for image generation
Handles model loading, LoRA integration, and generation pipeline
"""

import logging
import os
from typing import Optional, Dict, Any, Union
import torch
from diffusers import FluxPipeline
from safetensors.torch import load_file
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class FluxManager:
    """Manages FLUX model loading and generation"""
    
    def __init__(
        self,
        model_path: str,
        device: str = "cuda",
        dtype: torch.dtype = torch.float16
    ):
        self.model_path = model_path
        self.device = device
        self.dtype = dtype
        self.pipe: Optional[FluxPipeline] = None
        self.loaded_lora: Optional[str] = None
        self.is_ready = False
    
    async def initialize(self):
        """Initialize the FLUX pipeline"""
        try:
            logger.info(f"Loading FLUX model from {self.model_path}")
            
            # Load the pipeline
            self.pipe = FluxPipeline.from_pretrained(
                self.model_path,
                torch_dtype=self.dtype,
                use_safetensors=True,
                variant="fp16" if self.dtype == torch.float16 else None
            )
            
            # Move to device
            self.pipe = self.pipe.to(self.device)
            
            # Enable memory efficient attention if available
            if hasattr(self.pipe, "enable_xformers_memory_efficient_attention"):
                try:
                    self.pipe.enable_xformers_memory_efficient_attention()
                    logger.info("Enabled xformers memory efficient attention")
                except Exception as e:
                    logger.warning(f"Could not enable xformers: {e}")
            
            # Enable CPU offload for memory efficiency
            if self.device == "cuda" and torch.cuda.is_available():
                self.pipe.enable_sequential_cpu_offload()
                logger.info("Enabled sequential CPU offload")
            
            self.is_ready = True
            logger.info("FLUX model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FLUX model: {e}")
            raise
    
    def load_lora(self, lora_path: str, scale: float = 1.0):
        """Load a LoRA model for character consistency"""
        try:
            if not os.path.exists(lora_path):
                logger.error(f"LoRA file not found: {lora_path}")
                return False
            
            # Unload previous LoRA if different
            if self.loaded_lora and self.loaded_lora != lora_path:
                self.unload_lora()
            
            logger.info(f"Loading LoRA from {lora_path}")
            
            # Load LoRA weights
            lora_state_dict = load_file(lora_path)
            
            # Apply LoRA to the model
            self.pipe.load_lora_weights(
                lora_state_dict,
                adapter_name="character_lora"
            )
            
            # Set LoRA scale
            self.pipe.set_adapters(["character_lora"], adapter_weights=[scale])
            
            self.loaded_lora = lora_path
            logger.info(f"LoRA loaded successfully with scale {scale}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load LoRA: {e}")
            return False
    
    def unload_lora(self):
        """Unload the current LoRA model"""
        if self.loaded_lora:
            try:
                self.pipe.unload_lora_weights()
                self.loaded_lora = None
                logger.info("LoRA unloaded successfully")
            except Exception as e:
                logger.error(f"Failed to unload LoRA: {e}")
    
    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        lora_path: Optional[str] = None,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        width: int = 1024,
        height: int = 1024,
        seed: Optional[int] = None,
        **kwargs
    ) -> Image.Image:
        """
        Generate an image using FLUX
        
        Args:
            prompt: Text prompt for generation
            negative_prompt: Negative prompt
            lora_path: Path to LoRA model for character consistency
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale
            width: Image width
            height: Image height
            seed: Random seed
            
        Returns:
            Generated PIL Image
        """
        if not self.is_ready:
            raise RuntimeError("FLUX model not initialized")
        
        try:
            # Load LoRA if specified
            if lora_path and lora_path != self.loaded_lora:
                self.load_lora(lora_path)
            elif not lora_path and self.loaded_lora:
                self.unload_lora()
            
            # Set random seed for reproducibility
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            
            # Prepare generation parameters
            generation_kwargs = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "width": width,
                "height": height,
                "generator": generator,
            }
            
            # Add any additional kwargs
            generation_kwargs.update(kwargs)
            
            # Generate image
            logger.info(f"Generating image: {width}x{height}, steps: {num_inference_steps}")
            with torch.no_grad():
                result = self.pipe(**generation_kwargs)
            
            # Extract image from result
            if hasattr(result, 'images'):
                image = result.images[0]
            else:
                image = result
            
            logger.info("Image generation completed")
            return image
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.pipe:
                del self.pipe
                self.pipe = None
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.is_ready = False
            logger.info("FLUX manager cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        if torch.cuda.is_available():
            return {
                "allocated_gb": torch.cuda.memory_allocated() / 1024**3,
                "reserved_gb": torch.cuda.memory_reserved() / 1024**3,
                "free_gb": (torch.cuda.get_device_properties(0).total_memory - 
                           torch.cuda.memory_allocated()) / 1024**3
            }
        else:
            return {
                "allocated_gb": 0,
                "reserved_gb": 0,
                "free_gb": 0
            }
