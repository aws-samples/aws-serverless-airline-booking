FROM denvazh/gatling:latest
MAINTAINER Pawan Puthran (pputhran@amazon.com)

ENV COGNITO_CLIENT_ID 2hdal963uk66tjh5t8c4cpqn3e
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV USER_CSV user.csv
ENV GRAPHQL_URL "https://qz6v5gusl5e2xdcevlxrbxtgim.appsync-api.eu-west-2.amazonaws.com/graphql"
ENV API_URL "https://1rwnkmerpi.execute-api.eu-west-2.amazonaws.com/prod/charge"
ENV TOKEN_CSV user-with-token.csv

ADD ./data/user.csv /opt/gatling/user-files/resources
ADD ./test-scripts/* /opt/gatling/user-files/simulations/
ADD ./logback.xml /opt/gatling/conf