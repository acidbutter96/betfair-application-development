FROM python:3.10

WORKDIR /

COPY pyproject.txt ./
RUN pip install poetry
RUN poetry install

COPY . .

CMD [ "poetry", "run", "ipython"]