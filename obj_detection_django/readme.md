# Object Detection Django

## Setup
To run the object detection for django follow the below steps:
- Clone only files in [feature/obj-detection-django](https://github.com/ArhamSoft-Python-Team/videoObjectDetection/tree/feature/obj-detection-django/obj_detection_django)
- Create environment and install requirements :
  - Create virtual environment with: ```python -m venv env```
  - enable virtual environment with: ```source env/bin/activate```
  - install ```pip install -r requirements.txt```
 ## Running Server
-  Create DB migrations:
  - run ```python manage.py makemigrations```
  - run ```python manage.py migrate```
- run server with: ```python manage.py runserver```
