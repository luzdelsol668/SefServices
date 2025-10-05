FROM python:3.9-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PRODUCTION=1

WORKDIR /app

RUN apt-get update && apt-get -y install libpq-dev gcc \
    gcc \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    libglib2.0-dev

RUN apt-get install -y locales && \
    sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

ENV LANG=fr_FR.UTF-8
ENV LC_ALL=fr_FR.UTF-8

RUN apt-get update && apt-get install -y \
    libpangocairo-1.0-0 \
    libcairo2 \
    pango1.0-tools \
    libpango1.0-dev \
    fonts-freefont-ttf

RUN apt-get update && apt-get install -y supervisor && apt-get clean
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    xvfb  # Required for headless execution

COPY . /app

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN pip install --upgrade pip
RUN pip install --timeout=1000 --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --noinput

RUN python manage.py migrate

EXPOSE 8000

# Start supervisord as the main process
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]