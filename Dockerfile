#Dockerfile, Image, Container
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y apt-transport-https
RUN apt-get install tesseract-ocr-all -y
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install -r requirements.txt

COPY ./app .

CMD ["python", "./app_main.py"]