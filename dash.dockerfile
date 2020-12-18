FROM rocker/shiny

RUN apt-get update -qq && apt-get -y --no-install-recommends install \
    libxml2 \
    && install2.r --error \
    --deps TRUE \
    shinydashboard \
    tidyverse \
    leaflet \
    glue

COPY ./R/app.R /srv/shiny-server/scripts/
ADD data/output/ /srv/shiny-server/data/output/

EXPOSE 3838
CMD ["R", "-e", "shiny::runApp('/srv/shiny-server/scripts/app.R', port=3838, host='0.0.0.0')"]
