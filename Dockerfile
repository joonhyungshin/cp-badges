from python:3.12-alpine

WORKDIR /usr/src

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./docker-entrypoint.sh ./docker-entrypoint.sh

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh"]
