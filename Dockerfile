# 说明该镜像以哪个镜像为基础
FROM python:3.7-slim

RUN mkdir /youxiang
WORKDIR /youxiang

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
COPY . /youxiang

ENTRYPOINT ["python", "/youxiang/main.py"]
