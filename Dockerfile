FROM python:3.8.3-slim
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
WORKDIR /test-flask
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /test-flask
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
