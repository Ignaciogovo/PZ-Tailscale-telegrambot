FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proxy.py .

# Proxy corre como root para acceder al socket de Docker
# Aislado en red interna (pz-internal), solo acepta conexiones del bot
CMD ["python", "proxy.py"]
