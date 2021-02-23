# Instrumenting Django app with Uptrace

This is the original [Polls](https://docs.djangoproject.com/en/3.1/intro/tutorial01/) app
instrumented with Uptrace.

## Running with Docker

## Running locally

Install dependencies:

```shell
pip install -r requirements.txt
```

Update `django_postgres/settings.py` to connect to the local PostgreSQL server:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'example',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

```

Migrate database:

```shell
./manage.py migrate
```

Create superuser:

```shell
./manage.py createsuperuser
```

Start server:

```shell
./manage.py runserver
```

After that the Polls app should be available at http://127.0.0.1:8000/polls/.
