FROM denvazh/gatling:latest
MAINTAINER Pawan Puthran (pputhran@amazon.com)

ENV COGNITO_CLIENT_ID 2hdal963uk66tjh5t8c4cpqn3e
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV USER_CSV user.csv

ADD ./csv/user.csv /opt/gatling/user-files/resources
ADD ./gatling-scripts/* /opt/gatling/user-files/simulations/
ADD ./logback.xml /opt/gatling/conf