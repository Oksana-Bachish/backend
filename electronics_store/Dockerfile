FROM python:3.10-slim

WORKDIR /usr/src/electronics_store

RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y libpq-dev build-essential && apt-get install -y netcat-openbsd && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir media
ENV PYTHONUNBUFFERED=1

#RUN sed -i 's/\r$//g' /usr/src/electronics_store/entrypoint.sh  # настройка для windows перенос каретки
RUN dos2unix /usr/src/electronics_store/entrypoint.sh
RUN chown root:root /usr/src/electronics_store/entrypoint.sh
RUN chmod +x /usr/src/electronics_store/entrypoint.sh  # добавляем флаг -x(разрешение запуска)

ENTRYPOINT ["/usr/src/electronics_store/entrypoint.sh"]
