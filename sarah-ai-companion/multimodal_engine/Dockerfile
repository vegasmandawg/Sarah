FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install CUDA support (for GPU acceleration)
RUN apt-get update && apt-get install -y \
    nvidia-cuda-toolkit \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for models and outputs
RUN mkdir -p /app/models /app/lora_models /app/outputs /app/temp

# Copy application code
COPY . .

# Download base FLUX model (this will be cached in the image)
# Note: In production, models should be mounted as volumes
RUN python -c "from huggingface_hub import snapshot_download; \
    snapshot_download('black-forest-labs/FLUX.1-dev', \
    cache_dir='/app/models', \
    ignore_patterns=['*.md', '*.txt'])"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
