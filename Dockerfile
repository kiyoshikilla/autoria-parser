FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

RUN apt-get update && apt-get install -y postgres-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]