FROM python:3.7-slim

MAINTAINER Snow Wang <admin@farseer.vip>

WORKDIR /youxiang
COPY requirements.txt requirements.txt
COPY . /youxiang

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo '$TZ' > /etc/timezone && \
    pip install -r requirements.txt
    
ENTRYPOINT ["python", "/youxiang/main.py"]
