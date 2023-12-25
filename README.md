# ShopAI

It's an e-commerce app that has some AI functionalities

## SetUp of the project

- Step 1: I have created a repo on github and created a readme file and [.gitignore](.gitignore) file for python to ignore all the unnecessary files that we don't need them to be pushed to the repo.
- Step 2: I have created a [requirements.txt](requirements.txt) file that contains all the requirements that this project need to run.
- Step 3: I have created the [Dockerfile](Dockerfile) that contains the base image and the command that are going to be run and the user.

```
FROM python:3.12-alpine3.19

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

ENV PATH="/py/bin:$PATH"

USER django-user
```

- Step 4: I have created [.dockerignore](.dockerignore) to ignore all the unnecessary files of directory to make the docker image as light as possible.
- Step 5: I have created the [app](app/) folder that will contains all the project.
- Step 5: Then to build my image I have run this command

```
docker build .
```

- Step 6: I have created a [docker-compose](docker-compose.yml) file to create the services.
- Step 7: Then I have run this command to build it

```
docker-compose build
```

- Step 8: I have created [requirements.dev.txt](requirements.dev.txt) i have added the linting package that we will use only in developement.
- Step 9: I have added this ligne in [docker-compose.yml](docker-compose.yml)

```
args:
    - DEV=true
```

- Step 10: I have added these lignes in the [Dockerfile](Dockerfile)

```
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
```

and i have added this

```
ARG DEV=false
```

and i have added this in the RUN

```
if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
fi && \
```

- Step 11: Then i have rebuilded it

```
docker-compose build
```

- Step 12: I have created a [.flake8](app/.flake8) file under app that i will use to specify which files to check for linting problems.
- Step 13: I have run my linting tools to test if it's installed correctly

```
docker-compose run --rm app sh -c "flake8"
```

- Step 14: I have created the django project

```
docker-compose run --rm app sh -c "django-admin startproject app ."
```

- Step 15: I have run the project to test it

```
docker-compose up
```

- Step 16: I have created the [.github](.github) folder
- Step 17: And I have created another folder under .github [workflows](.github/workflows)
- Step 18: I have created a file under workflows [checks.yml](.github/workflows/checks.yml)
- Step 19: I have created loged in to [my dockerhub account](https://hub.docker.com) and navigated to **My account** then **security**
  ![Dockerhub security account](readme_images/dockerhub.png "dockerhub my account security")
- Step 20: I have created an access token for the github action.
- Step 21: I have created a new secret in my repo
  ![Github Secret](readme_images/github_secret.png "github secrete")
- Step 22: I have staged and commit and push the project on my repo and created a new tag

```
git add .
git commit -m "Version v0.0"
git tag -a v0.0 -m "Release version v0.0
git push origin main
git push origin v0.0
```

- Step 23: I have added the db service in the [docker-compose.yml](docker-compose.yml)

```
db:
    image: postgres:16-alpine
    volumes:
      - dev-db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=shopAi
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root

volumes:
  dev-db-data:

```

and I have added the name and user and pass of the db in the app service to wait for the db service to be created and started and then start the app

```
environment:
      - DB_HOST=db
      - DB_NAME=shopAi
      - DB_USER=root
      - DB_PASS=root
    depends_on:
      - db
```

Then I have tested in by running

```
docker-compose up
```

- Step 24: I have installed the postgres adaptor inside my Docker env

```
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user
```

- Step 25: I have added the psycopg2 in [requirements.txt](requirements.txt)

```
docker-compose down
docker-compose build
```

- Step 26: I have connect my django project to the postgresql db using environment variables

```
import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgres',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS')

    }
}
```

- Step 27: I have created called [core](app/core)

```
docker-compose run --rm app sh -c "python manage.py startapp core"
```

- Step 28: Then i have delete the `test.py` file and `views.py` and created the [test](app/core/test) and I have created this file to initialize the folder [`__init__.py`](app/core/tests/__init__.py)
- Step 29: I have added the [core](app/core) app in the [settings.py](app/app/settings.py)
- Step 30: I have created a folder [management](app/core/management) and i have created a file under it [`__init__.py`](app/core/management/__init__.py) and I have created a folder under the management [commands](app/core/management/commands/) and a [`__init.py`](app/core/management/commands/__init__.py) file under the commands
- Step 31: I have created another file under the [commands](app/core/management/commands/) called [wait_for_db.py](app/core/management/commands/wait_for_db.py)
- Step 32: I have created a file under the [test](app/core/tests) called [test_commands.py](app/core/tests/test_commands.py)
- Step 33: I have implemented the logique for [wait_for_db.py](app/core/management/commands/wait_for_db.py) and Tested it by running

```
docker-compose run --rm app sh -c "python manage.py wait_for_db"
```

Step 34: I have added some content in the [docker-compose.yml](docker-compose.yml) to run `wait_for_db` and `migrate`

```
command: >
      sh -c "python manage.py wait_for_db &&
             python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
```

and run this command to test it

```
docker-compose down
docker-compose up
```

Step 35: create a test user for the model.

## Psycopg2

### Required packages

- C compiler
- python3-dev
- libpq-dev

### Equivalent of the required packages for Alpine

- postgresql-client
- build-base
- postgresql-dev
- musl-dev

### Docker cleanup

`build-base`, `postgresql-dev` and `musl-dev` are only need to install the psycopg2 so after install the package we will delete them to keep our Docker file very minimal.
