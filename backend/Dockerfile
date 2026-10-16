# syntax=docker/dockerfile:1.7

FROM python:3.15-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv

RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /build
COPY requirements.lock.txt ./
RUN python -m pip install --requirement requirements.lock.txt


FROM python:3.15-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --system --gid 10001 releaseguard \
    && useradd --system --uid 10001 --gid releaseguard --home-dir /app releaseguard

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=releaseguard:releaseguard app ./app
COPY --chown=releaseguard:releaseguard alembic ./alembic
COPY --chown=releaseguard:releaseguard alembic.ini ./
COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=5 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=2)"]

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
