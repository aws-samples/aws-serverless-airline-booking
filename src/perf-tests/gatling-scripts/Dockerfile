FROM denvazh/gatling:latest
MAINTAINER Pawan Puthran (pputhran@amazon.com)

RUN apk update
RUN apk add python3
RUN pip3 install awscli

ENV COGNITO_CLIENT_ID 2hdal963uk66tjh5t8c4cpqn3e
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV USER_CSV user.csv
ENV GRAPHQL_URL https://ktxb6n35anaw7kzru24clold2e.appsync-api.eu-west-1.amazonaws.com/graphql
ENV API_URL https://w7ifcw6ai5.execute-api.eu-west-1.amazonaws.com/prod/charge
ENV TOKEN_CSV user-with-token.csv
ENV AWS_REGION eu-west-1
ENV S3_BUCKET pputhran-load-test

ADD ./data/user.csv /opt/gatling/user-files/resources/
ADD ./setup-users.scala /opt/gatling/user-files/simulations/
ADD ./Airline.scala /opt/gatling/user-files/simulations/
ADD ./logback.xml /opt/gatling/conf
ADD ./run-gatling.sh /opt/gatling/run-gatling.sh
RUN chmod 777 /opt/gatling/run-gatling.sh

ENTRYPOINT [ "/opt/gatling/run-gatling.sh" ]