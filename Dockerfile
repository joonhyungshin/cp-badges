FROM python:3.6-alpine

# Install Poetry
RUN apk add curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
RUN /root/.poetry/bin/poetry config virtualenvs.create false

# Create project directory
RUN mkdir /app
WORKDIR /app/

# Install Python dependencies
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock
RUN /root/.poetry/bin/poetry install --no-root --no-dev

COPY cp_badges.py /app/cp_badges.py

EXPOSE 5000

CMD gunicorn -w 4 -b :5000 cp_badges:app
