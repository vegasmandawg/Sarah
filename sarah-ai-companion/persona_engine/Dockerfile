FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data for VADER sentiment analysis
RUN python -c "import nltk; nltk.download('vader_lexicon')"

# Copy application code
COPY . .

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Ollama in the background\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
\n\
# Wait for Ollama to be ready\n\
echo "Waiting for Ollama to start..."\n\
sleep 10\n\
\n\
# Pull the required model\n\
echo "Pulling DeepSeek model..."\n\
ollama pull mradermacher/DeepSeek-R1-Distill-Llama-8B-Abliterated-GGUF:Q4_K_M\n\
\n\
# Start the FastAPI application\n\
echo "Starting Persona Engine..."\n\
uvicorn main:app --host 0.0.0.0 --port 8000 --reload\n\
\n\
# Keep Ollama running\n\
wait $OLLAMA_PID' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start services
CMD ["/app/start.sh"]
