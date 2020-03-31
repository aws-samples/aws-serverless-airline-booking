FROM python:3
MAINTAINER Pawan Puthran (pputhran@amazon.com)

WORKDIR /usr/src/app

COPY setup-users.py load-flight-data.py cleanup.py requirements.txt user.csv ./

RUN pip3 install awscli
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "/usr/local/bin/python3" ]