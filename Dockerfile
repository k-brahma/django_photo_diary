FROM python:3.12

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements/ ./requirements/
RUN pip install -r requirements/prod.txt
