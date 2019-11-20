FROM python:3
MAINTAINER Pawan Puthran (pputhran@amazon.com)

WORKDIR /usr/src/app

COPY setup-users.py load-flight-data.py cleanup.py requirements.txt user.csv ./

RUN pip3 install awscli
RUN pip3 install -r requirements.txt


ENV COGNITO_CLIENT_ID 1speauvb3jmk9u6r6cab5g6r2c
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV GRAPHQL_URL https://7yn4qp3ixvb3dbk5mniyw7z7dq.appsync-api.eu-west-1.amazonaws.com/graphql
ENV API_URL https://131gwlntqj.execute-api.eu-west-1.amazonaws.com/prod/charge
ENV TOKEN_CSV user-with-token.csv
ENV AWS_REGION eu-west-1
ENV S3_BUCKET awsserverlessairline-twitchbase-20191114092725-loadtest
ENV USER_COUNT 2
ENV DURING_TIME 60
ENV USER_CSV user.csv
ENV FOLDERPATH ./
ENV USER_POOL_ID eu-west-1_PAUBwGJzW
ENV APPSYNC_API_KEY 2rkrryxqqfb5zcvvbrnprbx6y4
ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT [ "/usr/local/bin/python3" ]
# CMD [ "/usr/local/bin/python3", "./generate-token.py" ]
# CMD [ "/usr/local/bin/python3", "./load-flight-data.py" ]