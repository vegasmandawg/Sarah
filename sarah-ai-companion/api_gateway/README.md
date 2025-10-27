# API Gateway Service

## Description

The API Gateway service acts as the single entry point for all client requests to the Sarah AI Companion backend. It uses Nginx as a reverse proxy to route requests to the appropriate microservices based on URL paths. This abstraction layer provides a unified API interface while maintaining service isolation.

## Purpose and Architecture Role

- **Centralized Routing**: Routes incoming requests to the correct microservice based on URL patterns
- **WebSocket Support**: Handles WebSocket connections for real-time chat functionality
- **Load Balancing Ready**: Can be extended to support load balancing across multiple service instances
- **Security Layer**: Can be enhanced with authentication, rate limiting, and other security features
- **Request/Response Modification**: Can add headers, modify requests, or handle CORS

## Configuration

### Environment Variables

No environment variables are required for the basic API Gateway configuration. The service uses the Docker network DNS to resolve service names.

### Running Locally

1. Ensure Docker is installed on your system
2. Build the Docker image:
   ```bash
   docker build -t sarah-api-gateway .
   ```
3. Run the container:
   ```bash
   docker run -p 8080:80 --name sarah-api-gateway sarah-api-gateway
   ```

### Running with Docker Compose

The API Gateway is configured in the main `docker-compose.yml` file. It will start automatically when you run:
```bash
docker-compose up api_gateway
```

## API Routes

The API Gateway routes requests to the following endpoints:

### Frontend Routes
- `GET /` - Proxies to the Next.js frontend application
- `GET /*` - All other routes default to the frontend

### WebSocket Endpoints
- `WS /ws/chat` - WebSocket connection for real-time chat with the Persona Engine

### Persona Engine Routes
- `POST /api/chat` - Send chat messages to the Persona Engine
- `GET /api/sentiment` - Analyze sentiment of text

### Multimodal Engine Routes
- `POST /api/generate/image` - Generate images using FLUX.1
- `POST /api/generate/voice` - Generate voice audio using TTS

### Memory Subsystem Routes
- `GET/POST /api/memory` - Memory CRUD operations
- `POST /api/retrieve-context` - Retrieve relevant context for conversations

### Character Manager Routes
- `GET/POST/PUT/DELETE /api/characters` - Character management operations

### Health Check Endpoints
- `GET /health` - API Gateway health check
- `GET /api/health/persona` - Persona Engine health check
- `GET /api/health/multimodal` - Multimodal Engine health check
- `GET /api/health/memory` - Memory Subsystem health check
- `GET /api/health/characters` - Character Manager health check

## Nginx Configuration Details

The `nginx.conf` file includes:
- **Client Settings**: 100MB max body size for large file uploads
- **Timeout Settings**: Extended timeouts for long-running operations (image generation, etc.)
- **WebSocket Support**: Proper headers for WebSocket upgrade
- **Upstream Definitions**: Service discovery using Docker network DNS
- **Proxy Headers**: X-Real-IP and X-Forwarded headers for proper client identification

## Extending the Gateway

To add a new route:
1. Define the upstream service in the `upstream` block
2. Add a new `location` block with the route pattern
3. Configure proxy settings and any special requirements (timeouts, headers, etc.)

Example:
```nginx
location /api/new-service {
    proxy_pass http://new_service:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Troubleshooting

- **502 Bad Gateway**: Check if the target service is running and accessible
- **504 Gateway Timeout**: Increase timeout values for long-running operations
- **WebSocket Connection Failed**: Ensure upgrade headers are properly configured
- **CORS Issues**: Add appropriate CORS headers in the location blocks if needed
