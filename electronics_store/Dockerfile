FROM python:3.10-slim

WORKDIR /usr/src/electronics_store

RUN apt-get update && apt-get install -y libpq-dev build-essential && apt-get install -y netcat-openbsd


RUN mkdir media

ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN sed -i 's/\r$//g' /usr/src/electronics_store/entrypoint.sh  # настройка для windows перенос каретки
RUN chmod +x /usr/src/electronics_store/entrypoint.sh  # добавляем флаг -x(разрешение запуска)

ENTRYPOINT ["./entrypoint.sh"]