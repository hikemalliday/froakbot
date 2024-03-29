FROM python:3.8.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get -y install tesseract-ocr \
  && apt-get install -y python3 python3-distutils python3-pip \
  && pip3 --no-cache-dir install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

RUN apt update \
  && apt-get install ffmpeg libsm6 libxext6 -y
RUN pip3 install pytesseract
RUN pip3 install opencv-python
RUN pip3 install pillow

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["main.py"]

# FROM python:3.8.10-slim

# WORKDIR /app

# COPY . /app/

# EXPOSE 8000

# RUN pip install -r requirements.txt

# CMD ["python", "/app/main.py"]