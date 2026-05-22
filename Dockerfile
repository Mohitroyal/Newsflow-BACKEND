FROM python:3.11-slim

# Create a non-root user for Hugging Face Spaces
RUN useradd -m -u 1000 user

# Install system dependencies for Playwright, WeasyPrint, and Unicode Fonts
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    librandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libasound2 \
    libpangocairo-1.0-0 \
    build-essential \
    python3-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    fonts-noto-core \
    fonts-noto-telugu \
    fonts-noto-devanagari \
    fonts-noto-kannada \
    fonts-noto-tamil \
    fonts-noto-malayalam \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps

COPY . .

# Set permissions for HF space user
RUN chown -R user:user /app
USER user

# Hugging Face spaces expect port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
