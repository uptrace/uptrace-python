FROM python:3

COPY . /src/
WORKDIR /src/example/flask

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "make", "run" ]
