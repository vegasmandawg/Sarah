# Multimodal Engine Service

## Description

The Multimodal Engine is a dedicated, unmoderated service for all non-text generation in the Sarah AI Companion system. It houses a high-fidelity, character-consistent image pipeline using FLUX.1 and an expressive voice synthesis module using ElevenLabs API.

## Purpose and Architecture Role

- **Image Generation**: Self-hosted FLUX.1 model for unmoderated image creation
- **Character Consistency**: LoRA-based system for maintaining visual character identity
- **Voice Synthesis**: Integration with ElevenLabs for high-quality, emotionally expressive TTS
- **Prompt Optimization**: LLM-driven prompt enhancement for better image quality
- **Emotion Injection**: Dynamic text preprocessing for more natural voice synthesis

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Service Configuration
SERVICE_NAME=multimodal_engine
SERVICE_PORT=8000

# Model Configuration
FLUX_MODEL_PATH=/app/models/black-forest-labs/FLUX.1-dev
DEVICE=cuda
USE_FP16=true

# Generation Defaults
DEFAULT_INFERENCE_STEPS=30
DEFAULT_GUIDANCE_SCALE=7.5
DEFAULT_NEGATIVE_PROMPT=bad anatomy, blurry, low quality...

# LoRA Configuration
LORA_OUTPUT_DIR=/app/lora_models
MIN_LORA_IMAGES=5
MAX_LORA_IMAGES=50

# Output Configuration
OUTPUT_DIR=/app/outputs
TEMP_DIR=/app/temp
AUTO_CLEANUP=true
CLEANUP_DELAY=3600

# ElevenLabs Configuration
ELEVENLABS_API_URL=https://api.elevenlabs.io/v1
ELEVENLABS_API_KEY=your_api_key_here
DEFAULT_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# External Services
PERSONA_ENGINE_URL=http://persona_engine:8000

# Memory Limits
MAX_IMAGE_SIZE=2048
MAX_BATCH_SIZE=4

# Logging
LOG_LEVEL=INFO
```

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Download FLUX.1 model:
   ```python
   from huggingface_hub import snapshot_download
   snapshot_download(
       "black-forest-labs/FLUX.1-dev",
       cache_dir="./models"
   )
   ```

3. Start the service:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Running with Docker Compose

The service is configured in the main `docker-compose.yml` file:
```bash
docker-compose up multimodal_engine
```

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns service health and GPU status

### Image Generation
- **POST** `/generate/image`
  - Request:
    ```json
    {
      "prompt": "A beautiful sunset over mountains",
      "negative_prompt": "blurry, low quality",
      "character_lora_id": "sarah_v1",
      "width": 1024,
      "height": 1024,
      "num_inference_steps": 30,
      "guidance_scale": 7.5,
      "seed": 42
    }
    ```
  - Response:
    ```json
    {
      "image_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "550e8400-e29b-41d4-a716-446655440000.png",
      "prompt": "sarah, photorealistic portrait of a woman...",
      "width": 1024,
      "height": 1024,
      "url": "/outputs/550e8400-e29b-41d4-a716-446655440000.png",
      "timestamp": "2024-01-01T00:00:00Z"
    }
    ```

### Voice Generation
- **POST** `/generate/voice`
  - Request:
    ```json
    {
      "text": "Hello, I'm Sarah! How can I help you today?",
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "stability": 0.5,
      "similarity_boost": 0.5,
      "style": 0.0
    }
    ```
  - Response:
    ```json
    {
      "audio_id": "660e8400-e29b-41d4-a716-446655440000",
      "filename": "660e8400-e29b-41d4-a716-446655440000.mp3",
      "text": "Hello, I'm Sarah! How can I help you today?",
      "enhanced_text": "[warmly] Hello, I'm Sarah! How can I help you today?",
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "url": "/outputs/660e8400-e29b-41d4-a716-446655440000.mp3",
      "duration_seconds": 3.5,
      "timestamp": "2024-01-01T00:00:00Z"
    }
    ```

### LoRA Training (Internal)
- **POST** `/train-lora`
  - Multipart form data with:
    - `character_id`: Character identifier
    - `images`: Multiple image files (5-50)
    - `trigger_word`: Trigger word for the LoRA
  - Response:
    ```json
    {
      "training_id": "sarah_12345678",
      "status": "training_started",
      "character_id": "sarah",
      "trigger_word": "sarah",
      "estimated_time_minutes": 15,
      "timestamp": "2024-01-01T00:00:00Z"
    }
    ```

### File Access
- **GET** `/outputs/{filename}`
  - Serves generated images and audio files

## Key Components

### FLUX Manager
- Handles FLUX.1 model loading and inference
- Manages LoRA loading/unloading for character consistency
- Implements memory-efficient generation with CPU offloading
- Supports xformers for optimized attention

### Prompt Optimization
- Uses Persona Engine LLM to enhance simple prompts
- Adds artistic style cues and quality markers
- Injects character LoRA trigger words
- Maintains prompt coherence and quality

### LoRA System
**Why LoRA over other methods:**
- **High Fidelity**: Deep identity capture vs. style transfer
- **Flexibility**: Works across diverse scenes and styles
- **Efficiency**: Small file size, fast switching between characters
- **Compatibility**: Well-supported by FLUX.1 architecture

### Voice Generation
- **Emotion Injection**: LLM preprocesses text to add emotional cues
- **ElevenLabs Integration**: High-quality, natural voice synthesis
- **Multiple Voices**: Support for different voice profiles per character
- **Real-time Generation**: Optimized for low-latency response

## Model Information

### FLUX.1 [dev]
- **Architecture**: Flow-based transformer model
- **Parameters**: 12B
- **Capabilities**: High-quality, diverse image generation
- **License**: Non-commercial use
- **Requirements**: ~16GB VRAM for fp16 inference

### Character LoRA
- **Rank**: 16 (balanced quality/size)
- **Target Modules**: Attention layers (to_k, to_q, to_v, to_out)
- **Training Images**: 5-50 per character
- **File Size**: ~50-100MB per LoRA

## Performance Considerations

### Image Generation
- **First Generation**: 30-60s (model loading)
- **Subsequent**: 10-20s for 1024x1024
- **Memory Usage**: 14-16GB VRAM
- **Optimization**: xformers, CPU offloading

### Voice Generation
- **Latency**: 1-3s for typical responses
- **Quality**: 24kHz, MP3 format
- **Emotion Processing**: <1s overhead

### LoRA Training
- **Duration**: 10-20 minutes
- **GPU Memory**: 20-24GB recommended
- **Batch Size**: 1-4 depending on GPU

## File Management

- **Auto-cleanup**: Generated files removed after 1 hour
- **Output Directory**: `/app/outputs` (in container)
- **Temporary Files**: `/app/temp` for training data
- **Model Cache**: `/app/models` (persistent volume)

## Troubleshooting

### Out of Memory Errors
- Enable CPU offloading
- Reduce batch size
- Use fp16 precision
- Lower image resolution

### Slow Generation
- Check GPU utilization
- Verify xformers installation
- Monitor CPU offloading overhead
- Consider upgrading GPU

### LoRA Issues
- Ensure sufficient training images
- Verify trigger word usage
- Check LoRA file integrity
- Monitor training loss

### Voice Generation Failures
- Verify ElevenLabs API key
- Check text length limits
- Monitor API quota
- Handle network timeouts
