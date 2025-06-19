FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_DIR=/code
ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PYTHONPATH=.

ENV VIRTUAL_ENV=${UV_PROJECT_ENVIRONMENT}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR ${UV_PROJECT_DIR}

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

COPY . ${UV_PROJECT_DIR}

CMD ["uv", "run", "python", "bs_int/manage.py", "runserver"]
