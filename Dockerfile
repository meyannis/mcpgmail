FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps if needed (uncomment as required)
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* requirements.txt* /app/
# Prefer requirements.txt if present; otherwise use pip on pyproject
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir .; fi

COPY . /app

# The server should support: python gmail_server.py --sse 0.0.0.0:8080
EXPOSE 8080
CMD ["python","gmail_server.py","--sse","0.0.0.0:8080"]
