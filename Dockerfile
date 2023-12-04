FROM python:3.8.10-slim

WORKDIR /app

COPY . /app/

EXPOSE 8000

RUN pip install -r requirements.txt

CMD ["python", "/app/main.py"]