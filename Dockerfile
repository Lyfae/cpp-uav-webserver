FROM shosoar/alpine-python-opencv
MAINTAINER Lyfae


WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install opencv-python-headless==4.5.3.56

COPY . .

EXPOSE  80

CMD [ "python", "./app.py" ]