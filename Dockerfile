FROM python:3
MAINTAINER Justin Neese
COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt
COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
