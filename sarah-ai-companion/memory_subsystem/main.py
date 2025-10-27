"""
Sarah AI Companion - Memory Subsystem Service
Hybrid memory system with PostgreSQL for facts and Milvus for semantic search
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from pymilvus import connections, Collection, utility
from sentence_transformers import SentenceTransformer

from database import get_db, init_db
from milvus_manager import MilvusManager
from models import (
    MemoryRetrievalRequest, MemoryRetrievalResponse,
    ConversationTurn, KeyFact, FactType
)
from memory_extractor import MemoryExtractor
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
redis_client: Optional[redis.Redis] = None
milvus_manager: Optional[MilvusManager] = None
sentence_model: Optional[SentenceTransformer] = None
memory_extractor: Optional[MemoryExtractor] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global redis_client, milvus_manager, sentence_model, memory_extractor
    
    # Startup
    logger.info("Starting Memory Subsystem...")
    
    # Initialize database
    await init_db()
    logger.info("PostgreSQL database initialized")
    
    # Initialize Redis
    try:
        redis_client = await redis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Connected to Redis")
        
        # Start background worker for conversation processing
        asyncio.create_task(conversation_worker())
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None
    
    # Initialize Milvus
    try:
        milvus_manager = MilvusManager(
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT
        )
        await milvus_manager.connect()
        await milvus_manager.create_collections()
        logger.info("Connected to Milvus")
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {e}")
        milvus_manager = None
    
    # Load sentence transformer model
    try:
        sentence_model = SentenceTransformer(settings.SENTENCE_MODEL_PATH)
        logger.info("Sentence transformer model loaded")
    except Exception as e:
        logger.error(f"Failed to load sentence transformer: {e}")
        sentence_model = None
    
    # Initialize memory extractor
    memory_extractor = MemoryExtractor(settings.PERSONA_ENGINE_URL)
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()
    if milvus_manager:
        milvus_manager.disconnect()
    logger.info("Memory Subsystem shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Sarah Memory Subsystem",
    description="Hybrid memory system for contextual conversation",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


async def conversation_worker():
    """Background worker to process conversation turns from Redis"""
    logger.info("Conversation worker started")

    while True:
        if not redis_client:
            logger.warning("Redis client unavailable, retrying conversation worker in 5s")
            await asyncio.sleep(5)
            continue

        try:
            # Subscribe to conversation turns
            pubsub = redis_client.pubsub()
            await pubsub.subscribe("conversation_turns")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await process_conversation_turn(data)
                    except Exception as e:
                        logger.error(f"Error processing conversation turn: {e}")

        except Exception as e:
            logger.error(f"Conversation worker error: {e}")
            await asyncio.sleep(5)  # Retry after delay


async def process_conversation_turn(data: Dict[str, Any]):
    """Process a conversation turn for memory extraction"""
    try:
        user_id = data["user_id"]
        character_id = data["character_id"]
        user_message = data["user_message"]
        ai_response = data["ai_response"]
        
        # Extract memories using LLM
        extracted_memories = await memory_extractor.extract_memories(
            user_message=user_message,
            ai_response=ai_response,
            user_id=user_id,
            character_id=character_id
        )
        
        # Store structured facts in PostgreSQL
        async with get_db() as db:
            for fact in extracted_memories.get("facts", []):
                await store_key_fact(
                    db=db,
                    user_id=user_id,
                    character_id=character_id,
                    fact_type=fact["type"],
                    fact_key=fact["key"],
                    fact_value=fact["value"]
                )
        
        # Generate embeddings for conversation
        if sentence_model:
            conversation_text = f"User: {user_message}\nAssistant: {ai_response}"
            embedding = sentence_model.encode(conversation_text).tolist()
            
            # Store in Milvus for semantic search
            if milvus_manager:
                await milvus_manager.insert_conversation(
                    user_id=user_id,
                    character_id=character_id,
                    text=conversation_text,
                    embedding=embedding
                )
        
        logger.info(f"Processed conversation turn for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to process conversation turn: {e}")


async def store_key_fact(
    db: AsyncSession,
    user_id: str,
    character_id: str,
    fact_type: str,
    fact_key: str,
    fact_value: str
):
    """Store a key fact in PostgreSQL"""
    from sqlalchemy import insert, update
    from database import key_facts_table
    
    # Check if fact already exists
    existing = await db.execute(
        key_facts_table.select().where(
            (key_facts_table.c.user_id == user_id) &
            (key_facts_table.c.character_id == character_id) &
            (key_facts_table.c.fact_key == fact_key)
        )
    )
    
    if existing.first():
        # Update existing fact
        await db.execute(
            update(key_facts_table).where(
                (key_facts_table.c.user_id == user_id) &
                (key_facts_table.c.character_id == character_id) &
                (key_facts_table.c.fact_key == fact_key)
            ).values(
                fact_value=fact_value,
                timestamp=datetime.utcnow()
            )
        )
    else:
        # Insert new fact
        await db.execute(
            insert(key_facts_table).values(
                user_id=user_id,
                character_id=character_id,
                fact_type=fact_type,
                fact_key=fact_key,
                fact_value=fact_value,
                timestamp=datetime.utcnow()
            )
        )
    
    await db.commit()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check PostgreSQL
    postgres_healthy = False
    try:
        async with get_db() as db:
            await db.execute(text("SELECT 1"))
            postgres_healthy = True
    except:
        pass
    
    # Check Milvus
    milvus_healthy = milvus_manager and milvus_manager.is_connected()
    
    # Check Redis
    redis_healthy = False
    if redis_client:
        try:
            await redis_client.ping()
            redis_healthy = True
        except:
            pass
    
    return {
        "status": "healthy" if all([postgres_healthy, milvus_healthy, redis_healthy]) else "degraded",
        "services": {
            "postgresql": "connected" if postgres_healthy else "disconnected",
            "milvus": "connected" if milvus_healthy else "disconnected",
            "redis": "connected" if redis_healthy else "disconnected",
            "sentence_model": "loaded" if sentence_model else "not_loaded"
        }
    }


@app.post("/retrieve-context", response_model=MemoryRetrievalResponse)
async def retrieve_context(
    request: MemoryRetrievalRequest,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve relevant context for a conversation"""
    try:
        # Parallel search in both databases
        facts_task = retrieve_key_facts(
            db=db,
            user_id=request.user_id,
            character_id=request.character_id,
            message=request.message
        )
        
        snippets_task = retrieve_conversation_snippets(
            user_id=request.user_id,
            character_id=request.character_id,
            message=request.message,
            limit=request.max_snippets or 5
        )
        
        # Wait for both searches
        relevant_facts, conversation_snippets = await asyncio.gather(
            facts_task, snippets_task
        )
        
        # Format context
        context_parts = []
        
        # Add key facts
        if relevant_facts:
            context_parts.append("=== Known Facts ===")
            for fact in relevant_facts:
                context_parts.append(f"- {fact['key']}: {fact['value']}")
            context_parts.append("")
        
        # Add conversation snippets
        if conversation_snippets:
            context_parts.append("=== Relevant Past Conversations ===")
            for snippet in conversation_snippets:
                context_parts.append(snippet)
                context_parts.append("---")
        
        context = "\n".join(context_parts) if context_parts else ""
        
        return MemoryRetrievalResponse(
            context=context,
            relevant_facts=relevant_facts,
            conversation_snippets=conversation_snippets
        )
        
    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def retrieve_key_facts(
    db: AsyncSession,
    user_id: str,
    character_id: str,
    message: str
) -> List[Dict[str, Any]]:
    """Retrieve relevant key facts from PostgreSQL"""
    from sqlalchemy import select, or_, func
    from database import key_facts_table
    
    # Extract potential entities from message (simplified)
    keywords = message.lower().split()
    
    # Search for facts containing keywords
    conditions = []
    for keyword in keywords:
        conditions.extend([
            func.lower(key_facts_table.c.fact_key).contains(keyword),
            func.lower(key_facts_table.c.fact_value).contains(keyword)
        ])
    
    if not conditions:
        return []
    
    result = await db.execute(
        select(key_facts_table).where(
            (key_facts_table.c.user_id == user_id) &
            (key_facts_table.c.character_id == character_id) &
            or_(*conditions)
        ).order_by(key_facts_table.c.timestamp.desc()).limit(10)
    )
    
    facts = []
    for row in result:
        facts.append({
            "type": row.fact_type,
            "key": row.fact_key,
            "value": row.fact_value,
            "timestamp": row.timestamp.isoformat()
        })
    
    return facts


async def retrieve_conversation_snippets(
    user_id: str,
    character_id: str,
    message: str,
    limit: int = 5
) -> List[str]:
    """Retrieve relevant conversation snippets from Milvus"""
    if not sentence_model or not milvus_manager:
        return []
    
    try:
        # Generate embedding for query
        query_embedding = sentence_model.encode(message).tolist()
        
        # Search in Milvus
        results = await milvus_manager.search_conversations(
            user_id=user_id,
            character_id=character_id,
            query_embedding=query_embedding,
            limit=limit
        )
        
        # Extract conversation texts
        snippets = [result["text"] for result in results]
        return snippets
        
    except Exception as e:
        logger.error(f"Failed to retrieve conversation snippets: {e}")
        return []


@app.post("/memory/facts")
async def create_fact(
    fact: KeyFact,
    db: AsyncSession = Depends(get_db)
):
    """Create or update a key fact"""
    await store_key_fact(
        db=db,
        user_id=fact.user_id,
        character_id=fact.character_id,
        fact_type=fact.fact_type,
        fact_key=fact.fact_key,
        fact_value=fact.fact_value
    )
    return {"status": "success", "message": "Fact stored successfully"}


@app.get("/memory/facts/{user_id}/{character_id}")
async def get_facts(
    user_id: str,
    character_id: str,
    fact_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all facts for a user/character combination"""
    from sqlalchemy import select
    from database import key_facts_table
    
    query = select(key_facts_table).where(
        (key_facts_table.c.user_id == user_id) &
        (key_facts_table.c.character_id == character_id)
    )
    
    if fact_type:
        query = query.where(key_facts_table.c.fact_type == fact_type)
    
    result = await db.execute(query.order_by(key_facts_table.c.timestamp.desc()))
    
    facts = []
    for row in result:
        facts.append({
            "fact_id": row.fact_id,
            "type": row.fact_type,
            "key": row.fact_key,
            "value": row.fact_value,
            "timestamp": row.timestamp.isoformat()
        })
    
    return {"facts": facts}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
