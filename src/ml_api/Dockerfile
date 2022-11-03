# pull official base image
FROM ubuntu:latest

# set working directory
WORKDIR /usr/src/ml_api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN apt update
RUN apt -y install python3-pip
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add src code
COPY api api

ENTRYPOINT ["uvicorn", "main:app", "--proxy-headers", "--forwarded-allow-ips", "*", "--host", "0.0.0.0", "--port", "80"]