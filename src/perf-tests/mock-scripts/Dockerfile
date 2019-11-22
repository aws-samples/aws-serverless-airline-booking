FROM python:3
MAINTAINER Pawan Puthran (pputhran@amazon.com)

WORKDIR /usr/src/app

COPY setup-users.py load-flight-data.py cleanup.py requirements.txt user.csv ./

RUN pip3 install awscli
RUN pip3 install -r requirements.txt


ENV COGNITO_CLIENT_ID 4o7m6870h4m3rgr0jmh94r98eu
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV GRAPHQL_URL https://cjrxt2mu4ven3batd5rlrnz36i.appsync-api.eu-west-1.amazonaws.com/graphql
ENV API_URL https://7ew4d2zmk5.execute-api.eu-west-1.amazonaws.com/prod/charge
ENV TOKEN_CSV user-with-token.csv
ENV AWS_REGION eu-west-1
ENV S3_BUCKET amplify-awsserverlessairline-twitchbase-172326-loadtest
ENV USER_COUNT 5
ENV DURING_TIME 300
ENV USER_CSV user.csv
ENV FOLDERPATH ./
ENV USER_POOL_ID eu-west-1_5Z3MA6mxd
ENV APPSYNC_API_KEY 7kgeiqgh5bcmfdnwojfvxtb2hm
ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT [ "/usr/local/bin/python3" ]
# CMD [ "/usr/local/bin/python3", "./generate-token.py" ]
# CMD [ "/usr/local/bin/python3", "./load-flight-data.py" ]