FROM continuumio/anaconda3

RUN apt-get update &\
    apt-get install --fix-missing -y xvfb xserver-xephyr libcairo2 firefox-esr

COPY . /app
RUN conda env create -f /app/env.yml
RUN pip install -e /app/data_science_toolkit/

ENV PATH /opt/conda/envs/aluguel/bin:$PATH
RUN /bin/bash -c "source activate aluguel"
# RUN tree /app

CMD ["python", "/app/run.py"]
