FROM python:3.9-alpine

RUN pip install pipenv

#Copy files needed 
COPY Pipfile.lock .
COPY src /app/src
COPY Pipfile .

#setting up dependencies
WORKDIR /app
RUN pipenv sync
RUN pipenv run pip freeze > ./requirements.txt
RUN pip install -r requirements.txt

#start gunicorn in application
WORKDIR /app/src
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]