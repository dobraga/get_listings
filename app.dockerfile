FROM continuumio/anaconda3

RUN apt-get update && apt-get install -y xvfb

RUN git clone https://github.com/dobraga/data_science_toolkit.git
RUN pip install -e data_science_toolkit/

COPY ./env.yml /
RUN conda env create -f env.yml

ENV PATH /opt/conda/envs/aluguel/bin:$PATH
RUN /bin/bash -c "source activate aluguel"

COPY ./aluguel /
# CMD ["python", "aluguel/run.py"]
