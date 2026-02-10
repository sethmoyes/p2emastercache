FROM python:3.11-slim

WORKDIR /app

# Copy everything
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir Flask gunicorn

# Expose port
EXPOSE 8080

# Run with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "bin.web.dungeon_turn_app:app"]
