"""
Sarah AI Companion - Character Manager Service
Handles character creation, management, and persona generation
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from database import get_db, init_db
from models import (
    CharacterCreateRequest, CharacterUpdateRequest, CharacterResponse,
    CharacterListResponse, PersonaGenerationRequest, PersonaGenerationResponse
)
from persona_generator import PersonaGenerator
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global persona generator
persona_generator: Optional[PersonaGenerator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global persona_generator
    
    # Startup
    logger.info("Starting Character Manager...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize persona generator
    persona_generator = PersonaGenerator(settings.PERSONA_ENGINE_URL)
    logger.info("Persona generator initialized")
    
    yield
    
    # Shutdown
    logger.info("Character Manager shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Sarah Character Manager",
    description="Character customization and management service",
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


async def trigger_lora_training(
    character_id: str,
    images: List[UploadFile],
    trigger_word: str = "sarah"
) -> Optional[str]:
    """Trigger LoRA training in the multimodal engine"""
    try:
        async with httpx.AsyncClient() as client:
            # Prepare form data
            files = []
            for idx, image in enumerate(images):
                content = await image.read()
                files.append(('images', (f'image_{idx}.png', content, 'image/png')))
                await image.seek(0)  # Reset file pointer
            
            response = await client.post(
                f"{settings.MULTIMODAL_ENGINE_URL}/train-lora",
                files=files,
                data={
                    "character_id": character_id,
                    "trigger_word": trigger_word
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"LoRA training started: {result['training_id']}")
                return result["training_id"]
            else:
                logger.error(f"LoRA training failed: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Failed to trigger LoRA training: {e}")
        return None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check database connection
    db_healthy = False
    try:
        async with get_db() as db:
            await db.execute(text("SELECT 1"))
            db_healthy = True
    except:
        pass
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "services": {
            "database": "connected" if db_healthy else "disconnected"
        }
    }


@app.post("/characters", response_model=CharacterResponse)
async def create_character(
    request: CharacterCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new character"""
    try:
        from sqlalchemy import insert
        from database import characters_table, users_table
        
        # Generate character ID
        character_id = f"{request.name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        # Ensure user exists
        user_result = await db.execute(
            users_table.select().where(users_table.c.user_id == request.user_id)
        )
        if not user_result.first():
            # Create user if doesn't exist
            await db.execute(
                insert(users_table).values(
                    user_id=request.user_id,
                    username=request.user_id,  # Default username
                    created_at=datetime.utcnow()
                )
            )
        
        # Generate enhanced persona if keywords provided
        persona_prompt = request.persona_prompt
        if not persona_prompt and (request.personality_traits or request.hobbies):
            generation_result = await generate_persona_from_keywords(
                personality_traits=request.personality_traits or [],
                hobbies=request.hobbies or []
            )
            persona_prompt = generation_result.persona_prompt
        
        # Create character
        result = await db.execute(
            insert(characters_table).values(
                character_id=character_id,
                user_id=request.user_id,
                name=request.name,
                persona_prompt=persona_prompt,
                voice_id=request.voice_id,
                appearance_seed=request.appearance_seed,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        
        await db.commit()
        
        logger.info(f"Created character: {character_id}")
        
        return CharacterResponse(
            character_id=character_id,
            user_id=request.user_id,
            name=request.name,
            persona_prompt=persona_prompt,
            voice_id=request.voice_id,
            appearance_seed=request.appearance_seed,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to create character: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/characters/with-images", response_model=CharacterResponse)
async def create_character_with_images(
    name: str = Form(...),
    user_id: str = Form(...),
    persona_prompt: Optional[str] = Form(None),
    voice_id: Optional[str] = Form(None),
    personality_traits: Optional[str] = Form(None),
    hobbies: Optional[str] = Form(None),
    images: List[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a character with reference images for LoRA training"""
    try:
        # Parse traits and hobbies from comma-separated strings
        traits_list = [t.strip() for t in personality_traits.split(",")] if personality_traits else []
        hobbies_list = [h.strip() for h in hobbies.split(",")] if hobbies else []
        
        # Create character request
        character_request = CharacterCreateRequest(
            name=name,
            user_id=user_id,
            persona_prompt=persona_prompt,
            voice_id=voice_id,
            personality_traits=traits_list,
            hobbies=hobbies_list
        )
        
        # Create character
        character = await create_character(character_request, db)
        
        # Trigger LoRA training if images provided
        if images and len(images) >= settings.MIN_LORA_IMAGES:
            training_id = await trigger_lora_training(
                character_id=character.character_id,
                images=images,
                trigger_word=name.lower().replace(" ", "_")
            )
            
            if training_id:
                # Update character with training ID
                from sqlalchemy import update
                from database import characters_table
                
                await db.execute(
                    update(characters_table)
                    .where(characters_table.c.character_id == character.character_id)
                    .values(appearance_seed=training_id)
                )
                await db.commit()
                
                character.appearance_seed = training_id
        
        return character
        
    except Exception as e:
        logger.error(f"Failed to create character with images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/characters/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific character"""
    try:
        from sqlalchemy import select
        from database import characters_table
        
        result = await db.execute(
            select(characters_table).where(
                characters_table.c.character_id == character_id
            )
        )
        
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return CharacterResponse(
            character_id=row.character_id,
            user_id=row.user_id,
            name=row.name,
            persona_prompt=row.persona_prompt,
            voice_id=row.voice_id,
            appearance_seed=row.appearance_seed,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/characters/user/{user_id}", response_model=CharacterListResponse)
async def list_user_characters(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List all characters for a user"""
    try:
        from sqlalchemy import select
        from database import characters_table
        
        result = await db.execute(
            select(characters_table)
            .where(characters_table.c.user_id == user_id)
            .order_by(characters_table.c.created_at.desc())
        )
        
        characters = []
        for row in result:
            characters.append(CharacterResponse(
                character_id=row.character_id,
                user_id=row.user_id,
                name=row.name,
                persona_prompt=row.persona_prompt,
                voice_id=row.voice_id,
                appearance_seed=row.appearance_seed,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))
        
        return CharacterListResponse(
            characters=characters,
            total=len(characters)
        )
        
    except Exception as e:
        logger.error(f"Failed to list characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/characters/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    request: CharacterUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update a character"""
    try:
        from sqlalchemy import update
        from database import characters_table
        
        # Build update values
        update_values = {"updated_at": datetime.utcnow()}
        
        if request.name is not None:
            update_values["name"] = request.name
        if request.persona_prompt is not None:
            update_values["persona_prompt"] = request.persona_prompt
        if request.voice_id is not None:
            update_values["voice_id"] = request.voice_id
        if request.appearance_seed is not None:
            update_values["appearance_seed"] = request.appearance_seed
        
        # Update character
        result = await db.execute(
            update(characters_table)
            .where(characters_table.c.character_id == character_id)
            .values(**update_values)
            .returning(characters_table)
        )
        
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Character not found")
        
        await db.commit()
        
        logger.info(f"Updated character: {character_id}")
        
        return CharacterResponse(
            character_id=row.character_id,
            user_id=row.user_id,
            name=row.name,
            persona_prompt=row.persona_prompt,
            voice_id=row.voice_id,
            appearance_seed=row.appearance_seed,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update character: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/characters/{character_id}")
async def delete_character(
    character_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a character"""
    try:
        from sqlalchemy import delete
        from database import characters_table
        
        # Delete character
        result = await db.execute(
            delete(characters_table)
            .where(characters_table.c.character_id == character_id)
        )
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Character not found")
        
        await db.commit()
        
        logger.info(f"Deleted character: {character_id}")
        
        return {"status": "success", "message": "Character deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete character: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/characters/generate-prompt", response_model=PersonaGenerationResponse)
async def generate_persona_from_keywords(
    personality_traits: List[str],
    hobbies: List[str]
):
    """Generate a rich persona prompt from keywords"""
    try:
        if not persona_generator:
            raise HTTPException(status_code=503, detail="Persona generator not available")
        
        request = PersonaGenerationRequest(
            personality_traits=personality_traits,
            hobbies=hobbies
        )
        
        result = await persona_generator.generate_persona(request)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
