FROM denvazh/gatling:latest
MAINTAINER Pawan Puthran (pputhran@amazon.com)

RUN apk update
RUN apk add python3
RUN pip3 install awscli

ENV COGNITO_CLIENT_ID 3bobvmq6k98mljio8ft6vvn9ka
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV GRAPHQL_URL https://yztnuxay65eo5ftfwaeimlc6ui.appsync-api.eu-west-1.amazonaws.com/graphql
ENV API_URL https://7pelqgp04d.execute-api.eu-west-1.amazonaws.com/prod/charge
ENV TOKEN_CSV user-with-token.csv
ENV AWS_REGION eu-west-1
ENV S3_BUCKET amplify-awsserverlessairline-twitchbase-170504-loadtest
ENV USER_COUNT 5
ENV DURING_TIME 300
ENV USER_CSV user.csv
ENV FOLDERPATH ./
ENV USER_POOL_ID eu-west-1_hewvNlih4
ENV APPSYNC_API_KEY bvzsntjcm5d4hiyujrculantg4
ENV PATH=/root/.local/bin:$PATH

ADD ./Airline.scala /opt/gatling/user-files/simulations/
ADD ./logback.xml /opt/gatling/conf
ADD ./run-gatling.sh /opt/gatling/run-gatling.sh
RUN chmod 777 /opt/gatling/run-gatling.sh

ENTRYPOINT [ "/opt/gatling/run-gatling.sh" ]