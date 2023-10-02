FROM python:3.9-alpine

RUN pip install pipenv

COPY Pipfile.lock .
COPY src /app/src
COPY Pipfile .
RUN pipenv sync
RUN pipenv run pip freeze > ./requirements.txt
RUN pip install -r requirements.txt

#start uvicorn in application
WORKDIR /app/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]