FROM --platform=linux/amd64 python:3.12-slim as build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-dev \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config && \
    apt-get install libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && pip install -r requirements.dev.txt

EXPOSE 8000

# Command to run on container start
CMD ["uvicorn", "application.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
