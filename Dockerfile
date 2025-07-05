FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN apt-get update && \
    apt-get install -y build-essential libgl1-mesa-glx curl && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["python", "main.py"]
