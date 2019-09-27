FROM python:3
MAINTAINER Pawan Puthran (pputhran@amazon.com)

WORKDIR /usr/src/app

COPY setup-users.py load-flight-data.py cleanup.py requirements.txt user.csv ./

RUN pip3 install -r requirements.txt

ENV COGNITO_CLIENT_ID 2hdal963uk66tjh5t8c4cpqn3e
ENV COGNITO_URL https://cognito-idp.eu-west-1.amazonaws.com/ 
ENV USER_CSV user.csv
ENV GRAPHQL_URL https://ktxb6n35anaw7kzru24clold2e.appsync-api.eu-west-1.amazonaws.com/graphql
ENV API_URL https://w7ifcw6ai5.execute-api.eu-west-1.amazonaws.com/prod/charge
ENV TOKEN_CSV user-with-token.csv
ENV PATH ./
ENV AWS_REGION eu-west-1
ENV USER_POOL_ID eu-west-1_BDDCLzdwo
ENV APPSYNC_API_KEY clab2lg6sba5td5pnfmtzfp25q
ENV S3_BUCKET pputhran-load-test

ENTRYPOINT [ "/usr/local/bin/python3" ]
# CMD [ "/usr/local/bin/python3", "./generate-token.py" ]
# CMD [ "/usr/local/bin/python3", "./load-flight-data.py" ]