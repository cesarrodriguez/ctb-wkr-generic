FROM 957723433972.dkr.ecr.sa-east-1.amazonaws.com/ctb-wkr-nottransac:dev-latest
COPY *.yml *.json /opt/ben/
WORKDIR /opt/ben