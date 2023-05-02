FROM python:3.8.9-slim-buster
COPY requirements.txt requirements.txt

WORKDIR .


RUN pip install pip --upgrade
RUN pip install setuptools --upgrade
COPY . .

RUN apt-get -y update && apt-get install -y autoconf autogen automake build-essential libasound2-dev \
  libflac-dev libogg-dev libtool libvorbis-dev libopus-dev libmp3lame-dev \
  libsndfile1-dev libgstreamer1.0-0 libcairo2-dev libgirepository1.0-dev libmpg123-dev pkg-config python && apt-get -y install ffmpeg


RUN pip3 install -r requirements.txt
ENV FLASK_APP=app.py

EXPOSE 5000

CMD python get_genre.py