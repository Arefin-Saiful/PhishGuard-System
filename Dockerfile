# ---------- base image ----------
FROM python:3.11-slim

# (optional) native build tools for NumPy / SciPy wheels
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# ---------- working directory ----------
WORKDIR /app

# ---------- Python deps ----------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ---------- project source ----------
COPY . .

# ---------- Gunicorn settings ----------
# • 1 worker keeps memory lowest (you can raise if your plan has more RAM)
# • 4 threads give a bit of concurrency
# • 120-second timeout lets the TensorFlow model finish loading on cold start
ENV GUNICORN_CMD_ARGS="--workers 1 --threads 4 --timeout 120"

# ---------- launch ----------
# Render injects $PORT at runtime; use 10000 when running locally.
CMD ["gunicorn", "-b", "0.0.0.0:${PORT:-10000}", "app:app"]
