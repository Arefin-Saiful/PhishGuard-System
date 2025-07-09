# ---------- base image ----------
FROM python:3.11-slim

# (optional) system build tools for numpy / scipy wheels
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---------- working directory ----------
WORKDIR /app

# ---------- install Python dependencies ----------
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------- copy project source ----------
COPY . .

# Render sets PORT at runtime; expose as env var
ENV PORT=10000

# ---------- launch ----------
CMD ["gunicorn", "-b", "0.0.0.0:${PORT}", "app:app"]
