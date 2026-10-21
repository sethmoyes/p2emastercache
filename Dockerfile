FROM python:3.13-slim

WORKDIR /app

# Dependencies first, so a code change doesn't reinstall them
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# The commit this image was built from, shown at /healthz:
#   fly deploy --build-arg GIT_SHA=$(git rev-parse --short HEAD)
ARG GIT_SHA=unknown
ENV GIT_SHA=$GIT_SHA

EXPOSE 8080

# Run with gunicorn. One worker so in-memory state (the merchant restock job,
# the dice jar) is shared by every request; threads handle concurrency.
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "1", "--threads", "8", "bin.web.dungeon_turn_app:app"]
