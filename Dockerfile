FROM python:latest

COPY src /app/src
COPY pyproject.toml /app/pyproject.toml

WORKDIR /app
RUN pip install -e .

ENTRYPOINT [ "axis-finder" ]
