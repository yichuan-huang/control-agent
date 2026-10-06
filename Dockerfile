# syntax=docker/dockerfile:1.7

FROM ghcr.io/astral-sh/uv:0.12.4 AS uv-bin

FROM debian:bookworm-slim AS python-base
ARG PYTHON_VERSION=3.12
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=${PYTHON_VERSION} \
    UV_LINK_MODE=copy \
    PATH=/opt/venv/bin:${PATH}
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=uv-bin /uv /uvx /usr/local/bin/
RUN uv python install "${PYTHON_VERSION}"
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --no-install-project
COPY . .
# Windows build contexts synthesize executable bits; Python modules are not executables.
RUN find /app -type f -name '*.py' -exec chmod 0644 {} +
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --no-editable && rm -rf /app/build

FROM node:24.21.0-bookworm-slim AS frontend-build
WORKDIR /app
COPY cfdc/web/frontend/package.json cfdc/web/frontend/pnpm-lock.yaml cfdc/web/frontend/pnpm-workspace.yaml cfdc/web/frontend/
RUN corepack enable \
    && corepack prepare pnpm@12.4.1 --activate \
    && pnpm --dir cfdc/web/frontend install --frozen-lockfile
COPY cfdc/web/frontend cfdc/web/frontend
COPY cfdc/resources/locales cfdc/resources/locales
RUN pnpm --dir cfdc/web/frontend run build

FROM debian:bookworm-slim AS app
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin cfdc
ENV PATH=/opt/venv/bin:${PATH} \
    HF_HOME=/home/cfdc/.cache/huggingface \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=python-base /opt/uv-python /opt/uv-python
COPY --from=python-base /opt/venv /opt/venv
COPY --from=python-base /app/cfdc /app/cfdc
COPY --from=python-base /app/app.py /app/main.py /app/pyproject.toml /app/uv.lock /app/LICENSE /app/
COPY --from=frontend-build /app/cfdc/web/frontend/dist /app/cfdc/web/frontend/dist
RUN mkdir -p /app/output /home/cfdc/.cache/huggingface \
    && chown -R cfdc:cfdc /app /home/cfdc
USER cfdc
EXPOSE 7860
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "7860"]

FROM python-base AS python-check
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-editable && rm -rf /app/build
CMD ["bash", "scripts/check_container.sh", "python"]

FROM python-check AS frontend-check
COPY --from=frontend-build /usr/local /usr/local
COPY --from=frontend-build /root/.cache/node/corepack /root/.cache/node/corepack
COPY --from=frontend-build /app/cfdc/web/frontend/node_modules /app/cfdc/web/frontend/node_modules
COPY --from=frontend-build /app/cfdc/web/frontend/dist /app/cfdc/web/frontend/dist
WORKDIR /app/cfdc/web/frontend
RUN pnpm exec playwright install --with-deps chromium
CMD ["bash", "/app/scripts/check_container.sh", "frontend"]
