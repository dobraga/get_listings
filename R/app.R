library(shinydashboard)
library(shiny)
library(tidyverse)
library(leaflet)

df <- readr::read_csv(
  "../data/output/apartamentos.csv", col_types = readr::cols()
) %>%
    mutate(
        html = paste(
        glue::glue(
            "<a onclick=\"window.open('{url}');\" href='#'> {title} </a>",
            url = url, title = title
        ),

        imagens %>% str_remove_all("\\[|\\]|\'|\"| ") %>% 
            str_split(",") %>% sapply(., function(x) x[1]) %>% 
            paste0("<img src='", ., "' width='300px' height='300px'>"),

        "<style> div.leaflet-popup-content {width:auto !important;}</style>",
        round(distance, 0), "metros de distância da estação", estacao
        )
    )

url_tile <- "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"


greenLeafIcon <- makeIcon(
    iconUrl = "http://leafletjs.com/examples/custom-icons/leaf-green.png",
    iconWidth = 38, iconHeight = 95,
    iconAnchorX = 22, iconAnchorY = 94,
    shadowUrl = "http://leafletjs.com/examples/custom-icons/leaf-shadow.png",
    shadowWidth = 50, shadowHeight = 64,
    shadowAnchorX = 4, shadowAnchorY = 62
)

preco_min <- min(df$preco_total, na.rm = T)
preco_max <- max(df$preco_total, na.rm = T)

quartos_max <- max(df$quartos, na.rm = T)

metragem_min <- min(df$metragem, na.rm = T)
metragem_max <- max(df$metragem, na.rm = T)

distance_min <- round(min(df$distance, na.rm = T), 0)
distance_max <- round(max(df$distance, na.rm = T), 0)

header <- dashboardHeader(title = "Aluguel")
sidebar <- dashboardSidebar(
    sliderInput(
        "preco", "Preço Total", min = preco_min, max = preco_max,
        value = c(preco_min, preco_max), step = 100
    ),
    sliderInput(
        "quartos", "Quantidade de Quartos", min = 1, max = quartos_max,
        value = c(1, quartos_max)
    ),
    sliderInput(
        "metragem", "Metragem (m²)", min = metragem_min, max = metragem_max,
        value = c(metragem_min, metragem_max)
    ),
    sliderInput(
        "distance", "Distância Metro (m²)", min = distance_min,
        max = distance_max, value = c(distance_min, distance_max)
    )
)
body <- dashboardBody(
    fluidPage(
        fluidRow(
            box(
                leafletOutput("leaflet", height = 1000),
                width = 12, height = 1000
            )
        )
    )
)

ui <- dashboardPage(
    header = header,
    sidebar = sidebar,
    body = body
)

server <- function(input, output) {
    df_react <- reactive({
        df %>% filter(
            between(preco_total, input$preco[1], input$preco[2]),
            between(quartos, input$quartos[1], input$quartos[2]),
            between(metragem, input$metragem[1], input$metragem[2]),
            between(distance, input$distance[1], input$distance[2]),
        )
    })

  output$leaflet <- renderLeaflet({
    leaflet() %>%
        addTiles(
            urlTemplate = url_tile
        ) %>%
        addMarkers(
            data = df_react(), lng = ~lng, lat = ~lat,
            popup = ~html, clusterOptions = markerClusterOptions()
        )
    })
}

shinyApp(ui, server)
