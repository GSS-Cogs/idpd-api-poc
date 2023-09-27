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

#start uvicorn in application
WORKDIR /app/src
CMD ["uvicorn", "main:app", "--reload"]