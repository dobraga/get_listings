FROM python:3.8

RUN apt-get update && apt-get install -y xvfb

RUN git clone https://github.com/dobraga/data_science_toolkit.git
RUN pip install -e data_science_toolkit/

COPY ./requirements.txt /
RUN pip install -r /requirements.txt
