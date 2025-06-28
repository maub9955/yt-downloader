FROM python:3.10-slim

# 1) ffmpeg 및 tor 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      tor && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) 애플리케이션 코드 복사
COPY . .

# 4) Tor 데몬과 Gunicorn을 함께 실행
CMD tor & \
    gunicorn app:app --bind 0.0.0.0:5000
