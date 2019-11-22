FROM python:3
MAINTAINER Pawan Puthran (pputhran@amazon.com)

WORKDIR /usr/src/app

COPY setup-users.py load-flight-data.py cleanup.py requirements.txt user.csv ./

RUN pip3 install awscli
RUN pip3 install -r requirements.txt


ENV COGNITO_CLIENT_ID 67pd6l637inlv78l7vigappvt2
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV GRAPHQL_URL https://uvq6oxlzb5gjdpu6nspj4qpj5y.appsync-api.eu-west-1.amazonaws.com/graphql
ENV API_URL https://5mxbat8wgj.execute-api.eu-west-1.amazonaws.com/prod/charge
ENV TOKEN_CSV user-with-token.csv
ENV AWS_REGION eu-west-1
ENV S3_BUCKET awsserverlessairline-twitchbase-20191121221048-loadtest
ENV USER_COUNT 5
ENV DURING_TIME 300
ENV USER_CSV user.csv
ENV FOLDERPATH ./
ENV USER_POOL_ID eu-west-1_O9uxFACs4
ENV APPSYNC_API_KEY sxpvwmdo6zdnfpih2arbs5runi
ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT [ "/usr/local/bin/python3" ]
# CMD [ "/usr/local/bin/python3", "./generate-token.py" ]
# CMD [ "/usr/local/bin/python3", "./load-flight-data.py" ]