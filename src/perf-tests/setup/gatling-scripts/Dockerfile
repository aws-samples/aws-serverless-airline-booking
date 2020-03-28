FROM denvazh/gatling:latest
MAINTAINER Pawan Puthran (pputhran@amazon.com)

RUN apk update
RUN apk add python3
RUN pip3 install awscli

ENV PATH=/root/.local/bin:$PATH

ADD ./Airline.scala /opt/gatling/user-files/simulations/
ADD ./logback.xml /opt/gatling/conf
ADD  queries/* /opt/gatling/queries/
ADD ./run-gatling.sh /opt/gatling/run-gatling.sh
RUN chmod 777 /opt/gatling/run-gatling.sh

ENTRYPOINT [ "/opt/gatling/run-gatling.sh" ]