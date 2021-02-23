FROM python:3

COPY . /src/
WORKDIR /src/example/django_postgres

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "make", "run" ]
