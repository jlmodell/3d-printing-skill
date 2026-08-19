FROM python:3.11-slim

# libgl1/libgomp1: runtime libs some build123d/OCP wheels dynamically link against.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 8123

# 0.0.0.0 here means "all interfaces INSIDE the container", which is required
# for the published port to reach it. It is not what controls host exposure --
# that is the 127.0.0.1 prefix on the port mapping in docker-compose.yml.
# Read that file's comment before changing either.
ENV HOST=0.0.0.0
ENV PORT=8123

CMD ["python", "server.py"]
