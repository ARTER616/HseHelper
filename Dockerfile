FROM python:3.9-slim
MAINTAINER Artyom Krasov "arter616@gmail.com"

WORKDIR /usr/src/bot

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "./main.py"]
