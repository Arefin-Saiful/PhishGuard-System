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

# ---------- launch ----------
# Render sets $PORT at runtime; provide 10000 as a local fallback
CMD sh -c 'gunicorn -b 0.0.0.0:${PORT:-10000} app:app'
