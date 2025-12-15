FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (cache)
COPY src/requirements.txt /app/requirements.txt

# Install deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app code + templates + static
COPY src/ /app/src/
COPY templates/ /app/templates/
COPY static/ /app/static/

EXPOSE 5000

# Run via gunicorn (production style)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "src.app:app"]