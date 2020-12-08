FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR movies_admin
EXPOSE 8000/tcp

COPY movies_admin/ .

RUN pip install --upgrade pip && pip install -r ./requirements/dev.txt
