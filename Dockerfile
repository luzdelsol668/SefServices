FROM python:3.9-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=fr_FR.UTF-8 \
    LC_ALL=fr_FR.UTF-8

WORKDIR /app

# System deps
RUN apt-get update && apt-get -y install \
    postgresql-client\
    libpq-dev gcc \
    libpango-1.0-0 libpangoft2-1.0-0 \
    libjpeg-dev libopenjp2-7-dev libffi-dev libglib2.0-dev \
    libpangocairo-1.0-0 libcairo2 pango1.0-tools libpango1.0-dev \
    fonts-freefont-ttf \
    wkhtmltopdf xvfb \
    postgresql-client \
    locales supervisor && \
    sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --timeout=1000 --no-cache-dir -r requirements.txt

COPY . /app
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Small wait script so the app starts only after DB is reachable
RUN printf '%s\n' '#!/bin/sh' \
  'echo "Waiting for Postgres $DB_HOST:${DB_PORT:-5432}...";' \
  'until pg_isready -h "${DB_HOST:-host.docker.internal}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" >/dev/null 2>&1; do sleep 2; done' \
  'echo "Postgres is ready."' \
  > /usr/local/bin/wait_for_db && chmod +x /usr/local/bin/wait_for_db

EXPOSE 8352

# NOTE: collectstatic & migrate will run at container start (see supervisor command)
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
