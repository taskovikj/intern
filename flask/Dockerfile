
# new docker

FROM python:3.8-slim-buster

# Install Git
RUN apt-get update && apt-get install -y git redis

WORKDIR /flask_app

# WORKDIR /usr/src/app/flask_app
RUN apt-get -y install gcc
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

# Expose the necessary port(s)
EXPOSE 5000






# older docker
# FROM python:3.8-slim-buster

# WORKDIR /flask_app

# # WORKDIR /usr/src/app/flask_app

# COPY requirements.txt requirements.txt

# RUN pip3 install -r requirements.txt

# COPY . .

# # CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]

