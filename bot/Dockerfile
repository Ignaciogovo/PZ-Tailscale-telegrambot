FROM python:3.11-slim

# Crear usuario no-root
RUN groupadd -r botuser && useradd -r -g botuser -d /home/botuser -s /sbin/nologin botuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cambiar permisos del directorio de trabajo
RUN chown -R botuser:botuser /app

# Correr como usuario no-root
USER botuser

CMD ["python", "bot.py"]
