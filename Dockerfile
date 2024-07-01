FROM python:3.12.3-alpine3.19 as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1

COPY ./requirements.txt .

RUN apk add --update --virtual .build-deps build-base g++ postgresql-dev gcc python3-dev libxml2-dev \
    libxslt-dev libffi-dev openssl-dev make cargo libpq git && \
    pip install --upgrade cffi pip setuptools && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt && \
    find /usr/local \
    \( -type d -a -name test -o -name tests \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    -exec rm -rf '{}' +

FROM python:3.12.3-alpine3.19

ARG NO_ROOT_USER="reseller"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

RUN apk add --update --no-cache libpq libxml2-dev libxslt-dev && \
    pip install --no-cache /wheels/* && \
    addgroup -S ${NO_ROOT_USER} && adduser -S ${NO_ROOT_USER} -G ${NO_ROOT_USER} -h /home/${NO_ROOT_USER} && \
    mkdir -p /home/${NO_ROOT_USER}/app

COPY . /home/${NO_ROOT_USER}/app

RUN chown -R ${NO_ROOT_USER}:${NO_ROOT_USER} /home/${NO_ROOT_USER}

USER ${NO_ROOT_USER}

WORKDIR /home/${NO_ROOT_USER}/app

EXPOSE 8080

CMD gunicorn reseller.wsgi --bind=0.0.0.0:8080 --workers=1
