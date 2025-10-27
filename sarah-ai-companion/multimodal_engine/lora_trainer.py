"""
LoRA Trainer for character-specific fine-tuning
Handles dataset preparation and LoRA training for FLUX models
"""

import logging
import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import torch
from PIL import Image
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType
from diffusers import FluxPipeline
from transformers import CLIPTokenizer
import numpy as np

logger = logging.getLogger(__name__)


class LoRATrainer:
    """Manages LoRA training for character consistency"""
    
    def __init__(
        self,
        base_model_path: str,
        output_dir: str,
        device: str = "cuda"
    ):
        self.base_model_path = base_model_path
        self.output_dir = output_dir
        self.device = device
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def prepare_dataset(
        self,
        image_paths: List[str],
        trigger_word: str,
        character_id: str
    ) -> Dataset:
        """
        Prepare dataset for LoRA training
        
        Args:
            image_paths: List of paths to training images
            trigger_word: Trigger word for the character
            character_id: Character identifier
            
        Returns:
            Prepared dataset
        """
        logger.info(f"Preparing dataset with {len(image_paths)} images")
        
        # Create captions for each image
        data = []
        for idx, image_path in enumerate(image_paths):
            # Generate varied captions with trigger word
            base_captions = [
                f"a photo of {trigger_word}",
                f"{trigger_word} in a portrait",
                f"a picture of {trigger_word}",
                f"{trigger_word} person",
                f"an image of {trigger_word}"
            ]
            
            caption = base_captions[idx % len(base_captions)]
            
            data.append({
                "image_path": image_path,
                "caption": caption,
                "character_id": character_id
            })
        
        # Create dataset
        dataset = Dataset.from_list(data)
        logger.info(f"Dataset prepared with {len(dataset)} samples")
        
        return dataset
    
    async def train(
        self,
        image_paths: List[str],
        output_path: str,
        trigger_word: str,
        character_id: str,
        num_train_epochs: int = 10,
        learning_rate: float = 1e-4,
        batch_size: int = 1
    ):
        """
        Train a LoRA for character consistency
        
        Args:
            image_paths: List of training image paths
            output_path: Path to save the trained LoRA
            trigger_word: Trigger word for the character
            character_id: Character identifier
            num_train_epochs: Number of training epochs
            learning_rate: Learning rate
            batch_size: Training batch size
        """
        try:
            logger.info(f"Starting LoRA training for character {character_id}")
            
            # Prepare dataset
            dataset = self.prepare_dataset(image_paths, trigger_word, character_id)
            
            # Load base model
            logger.info("Loading base model for training")
            pipe = FluxPipeline.from_pretrained(
                self.base_model_path,
                torch_dtype=torch.float16,
                use_safetensors=True
            ).to(self.device)
            
            # Configure LoRA
            lora_config = LoraConfig(
                r=16,  # Rank
                lora_alpha=32,
                target_modules=["to_k", "to_q", "to_v", "to_out.0"],
                lora_dropout=0.1,
                bias="none",
                task_type=TaskType.DIFFUSION_IMAGE_GENERATION,
            )
            
            # Apply LoRA to model
            pipe.unet = get_peft_model(pipe.unet, lora_config)
            
            # Training configuration
            training_args = {
                "num_train_epochs": num_train_epochs,
                "learning_rate": learning_rate,
                "batch_size": batch_size,
                "gradient_accumulation_steps": 4,
                "mixed_precision": "fp16",
                "save_steps": 100,
                "logging_steps": 10,
                "output_dir": os.path.dirname(output_path),
            }
            
            # Create optimizer
            optimizer = torch.optim.AdamW(
                pipe.unet.parameters(),
                lr=learning_rate,
                betas=(0.9, 0.999),
                weight_decay=0.01,
                eps=1e-08
            )
            
            # Training loop (simplified for demonstration)
            logger.info("Starting training loop")
            for epoch in range(num_train_epochs):
                epoch_loss = 0
                
                for idx, sample in enumerate(dataset):
                    # Load and preprocess image
                    image = Image.open(sample["image_path"]).convert("RGB")
                    image = image.resize((512, 512))  # Resize for training efficiency
                    
                    # Prepare inputs
                    inputs = pipe.feature_extractor(
                        images=image,
                        return_tensors="pt"
                    ).to(self.device)
                    
                    # Forward pass with caption
                    with torch.cuda.amp.autocast():
                        loss = self._compute_loss(
                            pipe,
                            inputs,
                            sample["caption"]
                        )
                    
                    # Backward pass
                    loss.backward()
                    
                    # Gradient accumulation
                    if (idx + 1) % training_args["gradient_accumulation_steps"] == 0:
                        optimizer.step()
                        optimizer.zero_grad()
                    
                    epoch_loss += loss.item()
                
                avg_loss = epoch_loss / len(dataset)
                logger.info(f"Epoch {epoch + 1}/{num_train_epochs}, Loss: {avg_loss:.4f}")
            
            # Save LoRA weights
            logger.info(f"Saving LoRA weights to {output_path}")
            pipe.unet.save_pretrained(output_path)
            
            # Save metadata
            metadata = {
                "character_id": character_id,
                "trigger_word": trigger_word,
                "num_images": len(image_paths),
                "num_epochs": num_train_epochs,
                "learning_rate": learning_rate
            }
            
            metadata_path = output_path.replace(".safetensors", "_metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("LoRA training completed successfully")
            
        except Exception as e:
            logger.error(f"LoRA training failed: {e}")
            raise
    
    def _compute_loss(
        self,
        pipe: FluxPipeline,
        inputs: Dict[str, torch.Tensor],
        caption: str
    ) -> torch.Tensor:
        """
        Compute training loss (simplified implementation)
        
        In production, this would implement proper diffusion training loss
        """
        # This is a placeholder - actual implementation would compute
        # the denoising loss for diffusion models
        return torch.tensor(0.1, requires_grad=True)
    
    def validate_lora(self, lora_path: str) -> bool:
        """Validate that a LoRA file is correctly formatted"""
        try:
            if not os.path.exists(lora_path):
                return False
            
            # Try to load the LoRA file
            from safetensors.torch import load_file
            weights = load_file(lora_path)
            
            # Check for expected keys
            required_keys = ["to_k", "to_q", "to_v"]
            has_required = any(
                any(req in key for req in required_keys)
                for key in weights.keys()
            )
            
            return has_required
            
        except Exception as e:
            logger.error(f"LoRA validation failed: {e}")
            return False
