# pull official base image
FROM python:3.8-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=$PYTHONPATH:./payments:/usr/lib/python3.8/site-packages

# copy dependencies file
COPY ./requirements.txt /usr/src/app/requirements.txt

# install psycopg dependencies, upgrade pip and install project dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev ;\
    pip install --upgrade pip ;\
    pip install -r requirements.txt --no-cache-dir --src /usr/src

# Add wait script to wait for mysql & redis
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait
RUN chmod +x /wait

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/
