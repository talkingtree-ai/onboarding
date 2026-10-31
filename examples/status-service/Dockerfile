# Versioned public image; review and update periodically. A tag is not a digest.
FROM python:3.12.16-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BIND_HOST=0.0.0.0 \
    PORT=8080 \
    DATA_DIR=/data

RUN groupadd --gid 10001 learner \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin learner \
    && mkdir /data /app \
    && chown 10001:10001 /data

WORKDIR /app
COPY --chown=0:0 app.py data_tool.py ./
USER 10001:10001
EXPOSE 8080
CMD ["python", "/app/app.py"]
