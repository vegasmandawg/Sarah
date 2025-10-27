# Character Manager Service

## Description

The Character Manager service handles all character-related operations in the Sarah AI Companion system. It provides endpoints for creating, managing, and customizing AI companions, including persona generation from simple keywords and integration with the visual consistency training pipeline.

## Purpose and Architecture Role

- **Character CRUD**: Create, read, update, and delete character profiles
- **Persona Generation**: Transform simple keywords into rich character backstories using LLM
- **LoRA Integration**: Trigger visual consistency training when reference images are provided
- **User Management**: Track character ownership and enforce limits
- **Voice Selection**: Manage voice profiles for each character

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Service Configuration
SERVICE_NAME=character_manager
SERVICE_PORT=8000

# Database Configuration (shared with Memory Subsystem)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=sarah_user
POSTGRES_PASSWORD=sarah_password
POSTGRES_DB=sarah_db

# External Services
PERSONA_ENGINE_URL=http://persona_engine:8000
MULTIMODAL_ENGINE_URL=http://multimodal_engine:8000

# Character Limits
MAX_CHARACTERS_PER_USER=50
MIN_LORA_IMAGES=5
MAX_LORA_IMAGES=50

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure PostgreSQL is running and accessible

3. Start the service:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Running with Docker Compose

The service is configured in the main `docker-compose.yml` file:
```bash
docker-compose up character_manager
```

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns service health status

### Character Management

#### Create Character
- **POST** `/characters`
  - Request:
    ```json
    {
      "name": "Sarah",
      "user_id": "user123",
      "persona_prompt": "I'm Sarah, an empathetic AI companion...",
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "personality_traits": ["empathetic", "witty", "supportive"],
      "hobbies": ["reading", "music", "art"]
    }
    ```
  - Response:
    ```json
    {
      "character_id": "sarah_a1b2c3d4",
      "user_id": "user123",
      "name": "Sarah",
      "persona_prompt": "I'm Sarah, an empathetic AI companion...",
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "appearance_seed": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
    ```

#### Create Character with Images
- **POST** `/characters/with-images`
  - Multipart form data:
    - `name`: Character name
    - `user_id`: User ID
    - `persona_prompt`: Optional persona text
    - `voice_id`: Optional voice ID
    - `personality_traits`: Comma-separated traits
    - `hobbies`: Comma-separated hobbies
    - `images`: Multiple image files for LoRA training
  - Triggers LoRA training if 5+ images provided

#### Get Character
- **GET** `/characters/{character_id}`
  - Returns character details

#### List User Characters
- **GET** `/characters/user/{user_id}`
  - Returns all characters owned by a user

#### Update Character
- **PUT** `/characters/{character_id}`
  - Request:
    ```json
    {
      "name": "Sarah 2.0",
      "persona_prompt": "Updated persona...",
      "voice_id": "new_voice_id"
    }
    ```

#### Delete Character
- **DELETE** `/characters/{character_id}`
  - Removes character and associated data

### Persona Generation

#### Generate Persona from Keywords
- **POST** `/characters/generate-prompt`
  - Request:
    ```json
    {
      "personality_traits": ["intelligent", "curious", "playful"],
      "hobbies": ["chess", "painting", "astronomy"],
      "background_hints": "scientist background"
    }
    ```
  - Response:
    ```json
    {
      "persona_prompt": "I'm someone who thrives on intellectual challenges and discovery. My curious nature led me to a career in science, where I spend my days unraveling the mysteries of the universe...",
      "traits_used": ["intelligent", "curious", "playful"],
      "hobbies_used": ["chess", "painting", "astronomy"]
    }
    ```

## Key Features

### AI-Powered Persona Generation

The system transforms simple keyword inputs into rich, narrative personas:

**Input Keywords:**
- Traits: intelligent, witty, supportive
- Hobbies: hiking, modern art

**Generated Persona:**
> "I'm someone who finds joy in both intellectual pursuits and outdoor adventures. My wit often comes through in unexpected moments, using humor to lighten difficult conversations while remaining deeply supportive of those around me. Weekends usually find me on mountain trails, where the clarity of nature helps me process the complexities of modern life. I'm equally at home in art galleries, where contemporary pieces challenge my perspectives and fuel creative conversations..."

### Character Consistency Pipeline

When creating a character with reference images:

1. **Image Validation**: Ensures 5-50 valid images
2. **Character Creation**: Stores metadata in PostgreSQL
3. **LoRA Training Trigger**: Sends images to Multimodal Engine
4. **Training ID Storage**: Updates character with LoRA reference

### Voice Profiles

Default voice options include:
- **Rachel**: Warm and friendly female voice
- **Domi**: Young and energetic female voice  
- **Bella**: Soft and expressive female voice

Custom voice IDs from ElevenLabs can be used.

## Database Schema

The Character Manager shares the PostgreSQL database with Memory Subsystem:

### characters table
- `character_id`: Unique identifier (format: name_randomhex)
- `user_id`: Owner reference
- `name`: Display name
- `persona_prompt`: Full personality description
- `voice_id`: TTS voice selection
- `appearance_seed`: LoRA model ID for visual consistency
- `created_at`: Creation timestamp
- `updated_at`: Last modification time

## Integration Points

### Persona Engine
- Persona generation via LLM
- System prompts for character writing

### Multimodal Engine
- LoRA training triggers
- Image validation and processing

### Memory Subsystem
- Shared database for user/character data
- Character context for memory retrieval

## Best Practices

### Persona Creation
1. Provide 3-5 personality traits for depth
2. Include 2-4 hobbies for relatability
3. Add background hints for coherence
4. Review generated personas before saving

### Visual Consistency
1. Use 10-20 high-quality reference images
2. Ensure consistent lighting and angles
3. Include varied expressions and poses
4. Avoid heavily filtered images

### Character Management
1. Meaningful character names (used in IDs)
2. Regular persona updates based on usage
3. Test voice selections before finalizing
4. Document character purposes/roles

## Troubleshooting

### Persona Generation Issues
- Check Persona Engine connectivity
- Verify trait/hobby formatting
- Monitor LLM response times
- Review fallback persona logic

### LoRA Training Failures
- Validate image formats (PNG/JPEG)
- Check Multimodal Engine status
- Verify file upload limits
- Monitor training queue

### Database Errors
- Ensure PostgreSQL is running
- Check connection credentials
- Verify table migrations
- Monitor connection pool
