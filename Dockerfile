FROM python:3.7-slim

MAINTAINER Snow Wang <admin@farseer.vip>

WORKDIR /youxiang
COPY requirements.txt requirements.txt
COPY . /youxiang

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo '$TZ' > /etc/timezone && \
    sed -i "s@http://deb.debian.org@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list && \
    apt-get update
RUN apt-get install -y libzbar-dev --fix-missing && \
    pip install -r requirements.txt
    
ENTRYPOINT ["python", "/youxiang/main.py"]
