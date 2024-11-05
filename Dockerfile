FROM python:3.11-slim


RUN sed -i 's@http://deb.debian.org@https://mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources; \
    apt-get update; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*


WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt \
    -i https://api.aiwaves.cn/pypi/simple \
    --trusted-host api.aiwaves.cn \
    --extra-index-url https://mirrors.aliyun.com/pypi/simple
