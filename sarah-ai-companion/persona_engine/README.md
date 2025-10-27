# Persona Engine Service

## Description

The Persona Engine is the core conversational AI service that houses Sarah's "soul" - the Large Language Model (LLM). This service manages all interactions with the uncensored DeepSeek model via Ollama, handles dynamic persona injection, and provides a real-time, streaming chat interface through WebSockets.

## Purpose and Architecture Role

- **LLM Integration**: Hosts and manages the DeepSeek-R1-Distill-Llama-8B-Abliterated model via Ollama
- **Dynamic Prompting**: Constructs prompts with compliance mandates, persona definitions, and context
- **Sentiment Analysis**: Uses VADER to analyze user sentiment and adjust response tone
- **Real-time Streaming**: Provides token-by-token streaming via WebSocket connections
- **Memory Publishing**: Publishes conversation turns to Redis for asynchronous memory processing

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Service Configuration
SERVICE_NAME=persona_engine
SERVICE_PORT=8000

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mradermacher/DeepSeek-R1-Distill-Llama-8B-Abliterated-GGUF:Q4_K_M
OLLAMA_TIMEOUT=300

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# External Services
CHARACTER_MANAGER_URL=http://character_manager:8000
MEMORY_SUBSYSTEM_URL=http://memory_subsystem:8000

# Generation Parameters
DEFAULT_TEMPERATURE=0.7
DEFAULT_TOP_P=0.9
MAX_TOKENS=2048

# WebSocket Configuration
WS_PING_INTERVAL=30
WS_PING_TIMEOUT=10

# Logging
LOG_LEVEL=INFO
```

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install and start Ollama:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama serve
   ```

3. Pull the required model:
   ```bash
   ollama pull mradermacher/DeepSeek-R1-Distill-Llama-8B-Abliterated-GGUF:Q4_K_M
   ```

4. Start the service:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Running with Docker Compose

The service is configured in the main `docker-compose.yml` file:
```bash
docker-compose up persona_engine
```

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns service health status and connectivity to dependencies

### Sentiment Analysis
- **POST** `/api/sentiment`
  - Request:
    ```json
    {
      "text": "I'm really excited about this!"
    }
    ```
  - Response:
    ```json
    {
      "compound": 0.8213,
      "positive": 0.678,
      "negative": 0.0,
      "neutral": 0.322
    }
    ```

### WebSocket Chat
- **WS** `/ws/chat`
  - Connection: `ws://localhost:8000/ws/chat`
  - Send Message:
    ```json
    {
      "message": "Hello Sarah!",
      "character_id": "default",
      "user_id": "user123"
    }
    ```
  - Receive Messages:
    ```json
    {
      "type": "status",
      "task": "processing_message"
    }
    ```
    ```json
    {
      "type": "token",
      "content": "Hello"
    }
    ```
    ```json
    {
      "type": "complete",
      "sentiment": {
        "compound": 0.5,
        "positive": 0.5,
        "negative": 0.0,
        "neutral": 0.5
      }
    }
    ```

## Key Components

### PromptManager
Handles dynamic prompt construction with three layers:
1. **Compliance Mandate**: Hardcoded instruction for uncensored behavior
2. **Persona Definition**: Character-specific personality from Character Manager
3. **Context Injection**: Memory snippets from Memory Subsystem

### Sentiment Analysis
Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) to:
- Analyze user message sentiment
- Adjust LLM temperature and top_p parameters
- Create emotionally appropriate responses

### Dynamic Tone Adjustment
- **Positive sentiment** (> 0.5): Increases temperature for creative responses
- **Negative sentiment** (< -0.3): Decreases temperature for focused replies
- **Neutral sentiment**: Uses default parameters

### WebSocket Communication
Provides real-time streaming with message types:
- `status`: Task updates (processing, generating)
- `token`: Individual response tokens
- `complete`: End of response with metadata
- `error`: Error messages

## Integration Points

### Character Manager
- Fetches character personas via HTTP
- Endpoint: `GET /characters/{character_id}`

### Memory Subsystem
- Retrieves contextual memories via HTTP
- Endpoint: `POST /retrieve-context`

### Redis
- Publishes conversation turns to `conversation_turns` channel
- Format:
  ```json
  {
    "user_id": "user123",
    "character_id": "default",
    "user_message": "Hello!",
    "ai_response": "Hi there!",
    "timestamp": 1234567890.123
  }
  ```

## Model Information

**DeepSeek-R1-Distill-Llama-8B-Abliterated-GGUF:Q4_K_M**
- Base: DeepSeek R1 architecture
- Size: 8B parameters
- Quantization: Q4_K_M (4-bit)
- Special: "Abliterated" - post-training modification to remove refusal behaviors
- Provider: Ollama via local installation

## Performance Considerations

- **Model Loading**: Initial model load can take 30-60 seconds
- **Memory Usage**: Requires ~8GB RAM for model + overhead
- **Streaming Latency**: First token typically appears within 1-2 seconds
- **Token Rate**: ~10-30 tokens/second depending on hardware

## Troubleshooting

### Ollama Connection Issues
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check model is downloaded: `ollama list`
- Ensure sufficient memory available

### WebSocket Disconnections
- Check client heartbeat implementation
- Verify nginx timeout settings in API Gateway
- Monitor memory usage during long conversations

### Slow Response Times
- Check sentiment analysis overhead
- Verify Redis connection for memory fetching
- Monitor Ollama GPU/CPU usage
