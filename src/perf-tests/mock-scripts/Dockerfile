FROM python:3
MAINTAINER Pawan Puthran (pputhran@amazon.com)

WORKDIR /usr/src/app

COPY setup-users.py load-flight-data.py cleanup.py requirements.txt user.csv ./

RUN pip3 install awscli
RUN pip3 install -r requirements.txt


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

ENTRYPOINT [ "/usr/local/bin/python3" ]
# CMD [ "/usr/local/bin/python3", "./generate-token.py" ]
# CMD [ "/usr/local/bin/python3", "./load-flight-data.py" ]