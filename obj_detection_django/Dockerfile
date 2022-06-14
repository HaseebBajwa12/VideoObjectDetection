# pull official base image
FROM python:3.8

# set work directory
WORKDIR /home/junaidafzal/Documents/"Junaid Afzal"/"my projects"/"objectdetection django"/projectfiles/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .