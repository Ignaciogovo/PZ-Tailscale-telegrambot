FROM python:3.11-slim

RUN groupadd -r proxyuser && useradd -r -g proxyuser -d /home/proxyuser -s /sbin/nologin proxyuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proxy.py .

RUN chown -R proxyuser:proxyuser /app

USER proxyuser

CMD ["python", "proxy.py"]
