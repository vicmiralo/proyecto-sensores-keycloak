# Usamos una imagen ligera de Python
FROM python:3.9-slim

# Creamos un directorio de trabajo
WORKDIR /app

# Instalamos FastAPI y Uvicorn (el servidor para Python)
# Instalamos dependencias para conectar con Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn psycopg2-binary

# Copiamos tu archivo de código al contenedor
COPY app.py .

# Exponemos el puerto 8000
EXPOSE 8000

# Comando para arrancar la API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]



