FROM python:3.10

WORKDIR /code

COPY ./pyproject.toml ./poetry.lock /code/

RUN pip install --no-cache-dir poetry && poetry config virtualenvs.in-project true && poetry install

COPY ./src /code/src

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
