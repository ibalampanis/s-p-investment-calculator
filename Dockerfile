FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8585

HEALTHCHECK CMD curl --fail http://localhost:8585/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8585", "--server.address=0.0.0.0"]
