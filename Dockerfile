ARG PYTHON_IMAGE=python:3.11-alpine3.24@sha256:09d17d5e4c16d0a7a1eea690bcb7c6ab8616b211f8421e429e97c1bef5bd0ed2
FROM ${PYTHON_IMAGE} AS build
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apk add --no-cache build-base cairo-dev jpeg-dev postgresql-dev libffi-dev libxml2-dev libxslt-dev
WORKDIR /build
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip wheel \
    && python -m pip install --ignore-installed --no-cache-dir --prefix=/install \
       --requirement requirements.txt setuptools==84.2.1 \
    && PYTHONPATH=/install/lib/python3.11/site-packages python -m pip check

FROM ${PYTHON_IMAGE} AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/app/.local/bin:${PATH}"
RUN apk add --no-cache curl cairo libjpeg-turbo libpq libstdc++ libxml2 libxslt \
    && python -m pip uninstall --yes pip wheel setuptools \
    && rm -rf /usr/local/lib/python3.11/ensurepip \
    && addgroup -S app \
    && adduser -S -G app -h /home/app app
COPY --from=build /install /usr/local
WORKDIR /app
COPY --chown=app:app . .
RUN chmod +x /app/docker-entrypoint.sh \
    && mkdir -p /app/media /app/static \
    && chown -R app:app /app
USER app
EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--timeout", "120", "CORE.wsgi:application"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
  CMD curl --fail --silent http://127.0.0.1:8000/ >/dev/null || exit 1
