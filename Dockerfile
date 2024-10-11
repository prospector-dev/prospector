FROM python:3
ADD . /prospector

RUN pip install /prospector mypy

WORKDIR /prospector
CMD prospector
