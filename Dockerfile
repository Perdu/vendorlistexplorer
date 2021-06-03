FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
MAINTAINER Célestin Matte <vendorlistexplorer@cmatte.me>

RUN apk add --update build-base python3 python3-dev mysql-client py3-mysqlclient bash wget netcat-openbsd busybox-initscripts && python3 -m ensurepip

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY download_import_vendorlists.sh /app/
COPY docker/* /app/
COPY docker/cronjob /etc/periodic/daily/
RUN chmod 0555 /etc/periodic/daily/cronjob
COPY static/ /app/static/
COPY templates/ /app/templates/
COPY *.py /app/
COPY config.conf.docker config.conf
RUN mv iabsite.py main.py
RUN chown -R nginx:root /app/
