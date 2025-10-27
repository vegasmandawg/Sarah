# Sarah AI Companion

A sophisticated multi-modal AI companion application featuring uncensored conversational AI, character customization, image generation, voice synthesis, and intelligent memory systems.

## 🚀 Overview

Sarah AI Companion is a full-stack application that creates personalized AI companions with unique personalities, visual appearances, and voices. Built with a microservices architecture, it combines cutting-edge AI technologies to deliver an immersive conversational experience.

### Key Features

- **Uncensored AI Conversations**: Powered by DeepSeek-R1-Distill-Llama-8B-Abliterated via Ollama
- **Dynamic Personalities**: Create companions with distinct traits, hobbies, and backstories
- **Visual Consistency**: LoRA-based character appearance training with FLUX.1
- **Voice Synthesis**: ElevenLabs integration for expressive text-to-speech
- **Intelligent Memory**: Hybrid PostgreSQL + Milvus system for perfect recall
- **Real-time Streaming**: WebSocket-based token-by-token response streaming
- **Sentiment Analysis**: VADER-based emotional intelligence

## 🏗️ Architecture

The application follows a microservices architecture with the following components:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│  API Gateway    │────▶│ Persona Engine  │
│   (Next.js)     │     │    (Nginx)      │     │   (Ollama)      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ├──────────────▶┌─────────────────┐
                                 │               │Multimodal Engine│
                                 │               │ (FLUX.1 + TTS)  │
                                 │               └─────────────────┘
                                 │
                                 ├──────────────▶┌─────────────────┐
                                 │               │Memory Subsystem │
                                 │               │(PostgreSQL+Milvus)│
                                 │               └─────────────────┘
                                 │
                                 └──────────────▶┌─────────────────┐
                                                 │Character Manager│
                                                 │  (CRUD + Gen)   │
                                                 └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Databases**: PostgreSQL 16, Milvus 2.3
- **AI Models**: 
  - LLM: DeepSeek-R1-Distill-Llama-8B (via Ollama)
  - Image: FLUX.1 [dev]
  - Embeddings: all-MiniLM-L6-v2
- **Real-time**: WebSockets, Redis Pub/Sub
- **Containerization**: Docker, Docker Compose

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Real-time**: Native WebSocket API
- **UI Components**: Custom design system

## 📋 Prerequisites

- Docker Desktop (with Docker Compose)
- 32GB+ RAM recommended
- NVIDIA GPU with 16GB+ VRAM (for FLUX.1)
- API Keys:
  - ElevenLabs API key (for voice synthesis)
  - HuggingFace token (for model downloads)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sarah-ai-companion.git
   cd sarah-ai-companion
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8080

## 📖 Service Documentation

Each service has comprehensive documentation:

- [API Gateway](./api_gateway/README.md) - Nginx reverse proxy configuration
- [Persona Engine](./persona_engine/README.md) - Conversational AI with Ollama
- [Multimodal Engine](./multimodal_engine/README.md) - Image and voice generation
- [Memory Subsystem](./memory_subsystem/README.md) - Hybrid memory system
- [Character Manager](./character_manager/README.md) - Character CRUD operations
- [Frontend](./frontend/README.md) - Next.js application

## 🔧 Configuration

### Essential Environment Variables

```env
# Database
POSTGRES_USER=sarah_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=sarah_db

# API Keys
ELEVENLABS_API_KEY=your_elevenlabs_key
HUGGINGFACE_TOKEN=your_hf_token

# Service Ports
API_GATEWAY_PORT=8080
FRONTEND_PORT=3000
```

### Memory Requirements by Service

| Service | Min RAM | Recommended | GPU |
|---------|---------|-------------|-----|
| Persona Engine | 8GB | 16GB | Optional |
| Multimodal Engine | 16GB | 32GB | Required (16GB+ VRAM) |
| Memory Subsystem | 4GB | 8GB | No |
| Character Manager | 2GB | 4GB | No |
| Frontend | 1GB | 2GB | No |

## 🎮 Usage Guide

### Creating Your First Companion

1. Navigate to http://localhost:3000
2. Click "Create New Character"
3. Fill in:
   - Name (e.g., "Sarah")
   - Select 3-5 personality traits
   - Choose hobbies (optional)
   - Generate or write a persona description
   - Upload reference images (optional, for visual consistency)
4. Click "Create Character"

### Starting a Conversation

1. Select your companion from the home screen
2. Click "Start Chatting"
3. Type your message and press Enter
4. Watch as responses stream in real-time
5. Notice sentiment indicators showing emotional tone

### Advanced Features

- **Voice Responses**: Enable in chat settings for TTS output
- **Image Generation**: Type "/imagine [description]" in chat
- **Memory Recall**: The AI automatically remembers past conversations

## 🔒 Security Considerations

- The Ollama model is uncensored - deploy responsibly
- Implement authentication before production deployment
- Use environment variables for all sensitive data
- Configure CORS appropriately for your domain
- Enable HTTPS for production deployments

## 🐛 Troubleshooting

### Common Issues

**Ollama Model Not Loading**
- Ensure sufficient RAM (8GB+ free)
- Check Ollama service logs: `docker logs sarah_persona_engine`
- Verify model download: `docker exec sarah_persona_engine ollama list`

**FLUX.1 Out of Memory**
- Requires 16GB+ VRAM
- Enable CPU offloading in configuration
- Reduce image resolution to 768x768

**WebSocket Connection Failed**
- Check API Gateway is running
- Verify nginx WebSocket configuration
- Ensure browser allows WebSocket connections

**Database Connection Issues**
- Wait for PostgreSQL to fully initialize
- Check credentials in .env match docker-compose.yml
- Verify Milvus dependencies (etcd, minio) are running

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install Python dependencies for a service
cd persona_engine
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
npm run dev
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DeepSeek** for the base R1 model
- **Black Forest Labs** for FLUX.1
- **ElevenLabs** for voice synthesis
- **Milvus** for vector database technology
- The open-source AI community

## 📞 Support

- Create an issue for bug reports
- Join our Discord community (coming soon)
- Check the [FAQ](docs/FAQ.md) for common questions

---

Built with ❤️ by the Sarah AI team
