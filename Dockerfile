ARG BASE_IMAGE=python:3.12-slim
FROM ${BASE_IMAGE} AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_DIR=/code
ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PYTHONPATH=.

ENV VIRTUAL_ENV=${UV_PROJECT_ENVIRONMENT}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /tmp/media_root
WORKDIR ${UV_PROJECT_DIR}

FROM base AS builder
# Install required packages and remove the apt packages cache when done.
RUN apt-get update && apt-get install -y \
        gnupg \
        g++ \
        git \
        apt-transport-https \
        ncurses-dev \
        libpq-dev \
        make && \
        pip install -U --no-cache-dir pip uv && \
        uv venv --seed ${VIRTUAL_ENV}

COPY uv.lock pyproject.toml ${UV_PROJECT_DIR}/

RUN uv sync --project ${UV_PROJECT_DIR}

FROM base AS final
RUN apt-get update && apt-get install -y \
        ncurses-dev \
        libpq-dev && \
        pip install -U pip uv
COPY pdbrc.py /root/.pdbrc.py
COPY . ${UV_PROJECT_DIR}

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

CMD ["uv", "run", "python", "bs_int/manage.py", "runserver"]
