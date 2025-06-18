ARG python_version=3.13

FROM python:${python_version}-alpine AS build

RUN apk add --no-cache uv

COPY requirements.txt /requirements.txt
ENV UV_TOOL_DIR=/app
RUN uv tool install --compile-bytecode --with-requirements=/requirements.txt gunicorn

FROM python:${python_version}-alpine
ARG python_version

# Only copy the necessary files from the build stage, to improve layer efficiency
COPY --from=build /app/gunicorn /app
COPY *.py  *.txt /app/bin/
COPY static /app/bin/static
COPY templates /app/bin/templates

RUN mkdir /config

RUN addgroup -S app --gid 1000 && adduser -S app --uid 1000 -G app
RUN chown -R app:app /config /app

USER app:app

VOLUME ["/config", "/app/bin/templates", "/app/bin/static"]

ENV PYTHONUNBUFFERED=1

WORKDIR /app/bin
ENTRYPOINT ["./python", "gunicorn", "--config", "/config/gunicorn.conf.py", "main:app"]
