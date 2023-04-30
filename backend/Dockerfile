FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip3 install pip --upgrade --no-cache-dir
RUN pip3 install -r requirements.txt --no-cache-dir

COPY backend/ .

CMD ["gunicorn", "foodgram_backend.wsgi:application", "--bind", "0:80" ]