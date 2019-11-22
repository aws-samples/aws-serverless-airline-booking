FROM denvazh/gatling:latest
MAINTAINER Pawan Puthran (pputhran@amazon.com)

RUN apk update
RUN apk add python3
RUN pip3 install awscli

ENV COGNITO_CLIENT_ID 67pd6l637inlv78l7vigappvt2
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV GRAPHQL_URL https://uvq6oxlzb5gjdpu6nspj4qpj5y.appsync-api.eu-west-1.amazonaws.com/graphql
ENV API_URL https://5mxbat8wgj.execute-api.eu-west-1.amazonaws.com/prod/charge
ENV TOKEN_CSV user-with-token.csv
ENV AWS_REGION eu-west-1
ENV S3_BUCKET awsserverlessairline-twitchbase-20191121221048-loadtest
ENV USER_COUNT 2
ENV DURING_TIME 60
ENV USER_CSV user.csv
ENV FOLDERPATH ./
ENV USER_POOL_ID eu-west-1_O9uxFACs4
ENV APPSYNC_API_KEY sxpvwmdo6zdnfpih2arbs5runi
ENV PATH=/root/.local/bin:$PATH

ADD ./Airline.scala /opt/gatling/user-files/simulations/
ADD ./logback.xml /opt/gatling/conf
ADD ./run-gatling.sh /opt/gatling/run-gatling.sh
RUN chmod 777 /opt/gatling/run-gatling.sh

ENTRYPOINT [ "/opt/gatling/run-gatling.sh" ]