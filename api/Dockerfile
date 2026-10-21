FROM python:3.10-slim

RUN useradd -s /bin/sh -u 1234 nonroot

WORKDIR /usr/src/electronics_store

RUN apt-get update && apt-get install -y libpq-dev build-essential && apt-get install -y netcat-openbsd

RUN pip install --upgrade pip

RUN mkdir media
RUN mkdir static

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

COPY . .

RUN sed -i 's/\r$//g' /usr/src/electronics_store/entrypoint.sh
RUN chmod +x /usr/src/electronics_store/entrypoint.sh

RUN chown -R nonroot:nonroot /usr/src/electronics_store
USER nonroot

ENTRYPOINT [ "./entrypoint.sh" ]