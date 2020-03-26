FROM denvazh/gatling:latest
MAINTAINER Pawan Puthran (pputhran@amazon.com)

RUN apk update
RUN apk add python3
RUN pip3 install awscli

ENV COGNITO_CLIENT_ID 6cg96ufuim7inubh9hcuh2ublp
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV GRAPHQL_URL https://vwax4foogzhtzbvkn2rtlgfmli.appsync-api.eu-west-1.amazonaws.com/graphql
ENV API_URL https://pa34ijh90g.execute-api.eu-west-1.amazonaws.com/prod/charge
ENV TOKEN_CSV user-with-token.csv
ENV AWS_REGION eu-west-1
ENV S3_BUCKET amplify-awsserverlessairline-twitchbase-84415-loadtest
ENV USER_COUNT 1
ENV DURING_TIME 60
ENV USER_CSV user.csv
ENV FOLDERPATH ./
ENV USER_POOL_ID eu-west-1_tOJAsWtF6
ENV APPSYNC_API_KEY 5bqhier6tjf2dnqytcnsa3sqsm
ENV PATH=/root/.local/bin:$PATH

ADD ./Airline.scala /opt/gatling/user-files/simulations/
ADD ./logback.xml /opt/gatling/conf
ADD  queries/* /opt/gatling/queries/
ADD ./run-gatling.sh /opt/gatling/run-gatling.sh
RUN chmod 777 /opt/gatling/run-gatling.sh

ENTRYPOINT [ "/opt/gatling/run-gatling.sh" ]