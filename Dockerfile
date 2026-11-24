FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
# Esquema para la base SQLite local de pruebas (sin DATABASE_URL). En produccion se usa PostgreSQL con DATABASE_URL.
COPY supabase/schema.sql ./supabase/schema.sql
# Dashboard del MVP: reutiliza archivos del prototipo. Se copian UNO A UNO a proposito: nunca prototipo/js/config.js (clave
# publica local) ni api.js. Streamlit queda fijo en requirements.txt (streamlit==1.65.0): el Dashboard usa st.iframe.
COPY prototipo/dashboard.html ./prototipo/dashboard.html
COPY prototipo/css/estilos.css prototipo/css/dashboard.css ./prototipo/css/
COPY prototipo/js/filtros.js prototipo/js/graficos.js prototipo/js/dashboard.js ./prototipo/js/
COPY prototipo/js/vendor/echarts.custom.min.js ./prototipo/js/vendor/echarts.custom.min.js

EXPOSE 8501

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
