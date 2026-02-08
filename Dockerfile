FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

RUN sudo apt-get update && sudo apt-get install -y postgresql-client && rm -rf /var/lib/lists/*

WORKDIR /app

COPY requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]