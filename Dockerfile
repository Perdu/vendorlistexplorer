FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
MAINTAINER Célestin Matte <vendorlistexplorer@cmatte.me>

RUN apk add --update build-base python3 python3-dev mysql-client py3-mysqlclient bash wget netcat-openbsd && python3 -m ensurepip

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . /app
COPY docker/* /app/
COPY iabsite.py main.py
COPY config.conf.docker config.conf

# CMD ["bash", "prestart.sh"]
CMD ["flask", "run"]
