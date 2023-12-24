# ShopAI

It's an e-commerce app that has some AI functionalities

## SetUp of the project

- Step 1: I have created a repo on github and created a readme file and [.gitignore](.gitignore) file for python to ignore all the unnecessary files that we don't need them to be pushed to the repo.
- Step 2: I have created a [requirements.txt](requirements.txt) file that contains all the requirements that this project need to run.
- Step 3: I have created the [Dockerfile](Dockerfile) that contains the base image and the command that are going to be run and the user.
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
