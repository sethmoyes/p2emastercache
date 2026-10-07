FROM python:3.13-slim

WORKDIR /app

# Copy everything
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir Flask gunicorn requests beautifulsoup4

# Expose port
EXPOSE 8080

# Run with gunicorn. One worker so in-memory state (the merchant restock job,
# the dice jar) is shared by every request; threads handle concurrency.
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "1", "--threads", "8", "bin.web.dungeon_turn_app:app"]
