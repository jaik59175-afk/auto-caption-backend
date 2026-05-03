# 1. Official Python image
FROM python:3.10-slim

# 2. Install FFmpeg and Git (Git is required for Whisper)
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# 3. Set Working Directory
WORKDIR /app

# 4. Copy requirements
COPY requirements.txt .

# FIX: Sabse pehle core tools ko ek specific purane version par lock kar do
# Isse Whisper ko build ke waqt pkg_resources mil jayega
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "setuptools<70.0.0" wheel

# Whisper ko alag se install karenge bina build isolate kiye
# Isse ye humare install kiye hue setuptools ko hi use karega
RUN pip install --no-cache-dir openai-whisper==20231117 --no-build-isolation

# Baaki saari requirements install karo
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy remaining code
COPY . .

# 6. Prepare directories
RUN mkdir -p uploads exports temp

# 7. Start Command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
