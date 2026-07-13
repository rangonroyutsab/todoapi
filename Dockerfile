FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    addgroup --system django && \ 
    adduser --system --ingroup django django && \
    mkdir -p /app/static && \
    chown -R django:django /app/static

COPY requirements.txt .
RUN pip install --only-binary :all: --no-cache-dir --require-hashes -r requirements.txt


COPY  ./todoapi/ /app/todoapi/
COPY  ./users/ /app/users/
COPY  ./manage.py /app/

USER django

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]