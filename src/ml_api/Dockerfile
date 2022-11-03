# pull official base image
FROM python:3.11

# set working directory
WORKDIR /usr/src/ml_api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install libhdf5-serial-dev netcdf-bin libnetcdf-dev \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add src code
COPY footy_ml .
COPY schemas.py .
COPY main.py .
COPY model_training_artifacts .

# train model
RUN python footy_ml/train.py

ENTRYPOINT ["uvicorn", "main:app", "--proxy-headers", "--forwarded-allow-ips", "*", "--host", "0.0.0.0", "--port", "80"]