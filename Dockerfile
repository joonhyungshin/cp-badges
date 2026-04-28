FROM python:3.12-alpine AS build

WORKDIR /usr/src/app

RUN apk add --no-cache build-base libffi-dev
RUN pip install poetry

RUN python -m venv /opt/venv
ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install

FROM python:3.12-alpine

WORKDIR /usr/src/app

RUN apk add --no-cache libffi

COPY --from=build /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
COPY . .

ENV PORT=8080

CMD litestar --app main:app run --host 0.0.0.0 --port $PORT

