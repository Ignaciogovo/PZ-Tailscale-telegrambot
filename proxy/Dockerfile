FROM python:3.11-slim

# Crear usuario no-root (por si se necesita en el futuro)
RUN groupadd -r proxyuser && useradd -r -g proxyuser -d /home/proxyuser -s /sbin/nologin proxyuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proxy.py .

RUN chown -R proxyuser:proxyuser /app

# NOTA: El proxy corre como root para acceder al socket de Docker
# Está aislado en red interna (pz-internal) y solo acepta conexiones del bot
CMD ["python", "proxy.py"]
