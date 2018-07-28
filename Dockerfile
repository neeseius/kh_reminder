FROM python:3
MAINTAINER Justin Neese
COPY . /kh_reminder
RUN pip install -r /kh_reminder/requirements.txt
RUN pip install -e /kh_reminder

CMD ["pserve", "/kh_reminder/development.ini", "--reload"]
