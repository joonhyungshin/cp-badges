from python:3.12-alpine

RUN pip install -U pip

WORKDIR /usr/src

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD fastapi run main.py --host 0.0.0.0 --port $PORT
