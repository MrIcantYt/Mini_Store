FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install colorama

CMD ["python", "-m", "mini_store"]
