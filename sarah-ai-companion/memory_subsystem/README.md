# Memory Subsystem Service

## Description

The Memory Subsystem provides Sarah's "heart" - a persistent, complex, and low-latency memory system that enables proactive, contextual conversation. It implements a hybrid architecture combining PostgreSQL for structured facts with Milvus for semantic vector search, providing both 100% accurate fact recall and contextually relevant conversation retrieval.

## Purpose and Architecture Role

- **Hybrid Storage**: PostgreSQL for atomic facts, Milvus for conversational embeddings
- **Intelligent Extraction**: LLM-powered memory extraction from conversations
- **Low-Latency Retrieval**: Optimized parallel search across both databases
- **Asynchronous Processing**: Background workers for memory ingestion
- **Contextual RAG**: Provides formatted context for persona engine prompts

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Service Configuration
SERVICE_NAME=memory_subsystem
SERVICE_PORT=8000

# PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=sarah_user
POSTGRES_PASSWORD=sarah_password
POSTGRES_DB=sarah_db

# Milvus Configuration
MILVUS_HOST=milvus
MILVUS_PORT=19530

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Model Configuration
SENTENCE_MODEL_PATH=/app/models/sentence-transformer
EMBEDDING_DIM=384

# External Services
PERSONA_ENGINE_URL=http://persona_engine:8000

# Memory Settings
MAX_FACTS_PER_USER=10000
MAX_CONVERSATIONS_PER_USER=50000
CONVERSATION_CHUNK_SIZE=500

# Performance Settings
BATCH_SIZE=100
WORKER_CONCURRENCY=4

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start PostgreSQL, Milvus, and Redis:
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:16
   docker-compose -f milvus-docker-compose.yml up -d
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. Initialize database:
   ```python
   from database import init_db
   import asyncio
   asyncio.run(init_db())
   ```

4. Start the service:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Running with Docker Compose

The service is configured in the main `docker-compose.yml` file:
```bash
docker-compose up memory_subsystem
```

## Database Schema

### PostgreSQL Tables

#### users
- `user_id` (PK): Unique user identifier
- `username`: User's display name
- `created_at`: Account creation timestamp

#### characters
- `character_id` (PK): Unique character identifier
- `user_id` (FK): Owner user ID
- `name`: Character name
- `persona_prompt`: Character personality definition
- `voice_id`: ElevenLabs voice ID
- `appearance_seed`: LoRA model identifier

#### key_facts
- `fact_id` (PK): Auto-incrementing ID
- `user_id` (FK): Associated user
- `character_id` (FK): Associated character
- `fact_type`: Type (preference, event, relationship, etc.)
- `fact_key`: Fact identifier (e.g., "favorite_color")
- `fact_value`: Fact content (e.g., "blue")
- `timestamp`: Last updated

### Milvus Collection

#### conversational_memories
- `embedding_id`: Unique identifier
- `user_id`: User ID
- `character_id`: Character ID
- `conversation_text`: Raw conversation text
- `embedding`: 384-dimensional vector
- `timestamp`: Creation time

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns service health and database connectivity

### Context Retrieval
- **POST** `/retrieve-context`
  - Request:
    ```json
    {
      "message": "Tell me about my project deadline",
      "user_id": "user123",
      "character_id": "sarah",
      "max_facts": 10,
      "max_snippets": 5
    }
    ```
  - Response:
    ```json
    {
      "context": "=== Known Facts ===\n- project_deadline: March 15th\n...",
      "relevant_facts": [
        {
          "type": "event",
          "key": "project_deadline",
          "value": "March 15th",
          "timestamp": "2024-01-01T00:00:00Z"
        }
      ],
      "conversation_snippets": [
        "User: When is my project due?\nAssistant: Your project deadline is March 15th."
      ]
    }
    ```

### Fact Management
- **POST** `/memory/facts`
  - Create or update a fact
  - Request:
    ```json
    {
      "user_id": "user123",
      "character_id": "sarah",
      "fact_type": "preference",
      "fact_key": "favorite_food",
      "fact_value": "pizza"
    }
    ```

- **GET** `/memory/facts/{user_id}/{character_id}`
  - Retrieve all facts for a user/character
  - Query params: `fact_type` (optional)

## Key Components

### Hybrid Architecture Benefits

**Why Not Pure Vector RAG?**
- Vector search excels at semantic similarity but can miss specific facts
- Example: "What's my dog's name?" might retrieve conversations about dogs but not the exact name
- Structured storage ensures 100% recall for atomic facts

**Architecture Advantages:**
1. **Accuracy**: Critical facts stored relationally for perfect recall
2. **Context**: Vector search provides relevant conversation history
3. **Speed**: Parallel queries to both databases
4. **Flexibility**: Can handle both specific queries and vague requests

### Memory Extraction Pipeline

1. **Conversation Published**: Persona Engine publishes to Redis
2. **Worker Processing**: Background worker consumes message
3. **LLM Extraction**: Intelligent parsing of conversation
4. **Dual Storage**: Facts to PostgreSQL, embeddings to Milvus

### Retrieval Strategy

1. **Parallel Search**: Simultaneous queries to both databases
2. **Keyword Extraction**: Identify entities in user message
3. **Vector Embedding**: Generate embedding for semantic search
4. **Result Fusion**: Combine and rank results
5. **Context Formatting**: Structure for LLM consumption

## Memory Types and Examples

### Key Facts (PostgreSQL)
- **Preferences**: "favorite_color" → "blue"
- **Events**: "birthday" → "June 15th"
- **Relationships**: "pet_name" → "Max"
- **Personal Info**: "occupation" → "software engineer"
- **Goals**: "fitness_goal" → "run a marathon"
- **Habits**: "morning_routine" → "coffee and meditation"

### Conversation Memories (Milvus)
- Full conversation turns with context
- Emotional moments and reactions
- Story narratives and experiences
- Opinions and thoughts expressed

## Performance Optimization

### Database Indexing
- PostgreSQL: Composite indexes on (user_id, character_id)
- Milvus: IVF_FLAT index for vector similarity

### Caching Strategy
- Redis for frequently accessed facts
- In-memory LRU cache for embeddings
- Connection pooling for databases

### Async Processing
- Non-blocking database queries
- Background memory extraction
- Concurrent retrieval operations

## Monitoring and Maintenance

### Metrics to Track
- Query latency (target: <100ms)
- Memory extraction success rate
- Database sizes and growth
- Vector search accuracy

### Maintenance Tasks
- Periodic fact deduplication
- Conversation pruning (old/irrelevant)
- Index optimization
- Backup procedures

## Troubleshooting

### Slow Retrieval
- Check database indexes
- Monitor Milvus collection load state
- Verify Redis connectivity
- Review query complexity

### Missing Memories
- Confirm Redis subscription active
- Check extraction worker logs
- Validate LLM extraction prompts
- Ensure database writes succeed

### High Memory Usage
- Review Milvus collection size
- Check sentence model caching
- Monitor worker queue depth
- Consider memory limits
