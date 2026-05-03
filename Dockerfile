# 1. Python install karne ke liye official base image
FROM python:3.10-slim

# 2. FFmpeg aur zaroori tools install karne ki command
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# 3. Server ke andar ek working directory set karna
WORKDIR /app

# 4. Requirements file copy karna aur libraries (Uvicorn, Whisper etc.) install karna
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Aapka baaki saara backend code server me copy karna
COPY . .

# 6. Zaroori folders banana taaki upload/export me error na aaye
RUN mkdir -p uploads exports temp

# 7. Uvicorn ke through FastAPI server start karne ki command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]