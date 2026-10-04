FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY chatgpt_space_broker.py yjs_crdt_sync_worker.py ./

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["python", "chatgpt_space_broker.py"]
