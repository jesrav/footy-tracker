# pull official base image
FROM python:3.9

# set working directory
WORKDIR /usr/src/api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .

ENTRYPOINT ["uvicorn", "main:app", "--proxy-headers", "--forwarded-allow-ips", "*", "--host", "0.0.0.0", "--port", "80"]