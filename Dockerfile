from python:3.12-alpine

RUN pip install -U pip

WORKDIR /usr/src

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./docker-entrypoint.sh ./docker-entrypoint.sh

COPY . .

CMD fastapi run main.py --host 0.0.0.0 --port $PORT
