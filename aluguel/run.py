from fetcher.imoveis import Imoveis
from fetcher.metro import MetroSpyder
from data.preprocess import preprocess
from config import Configurations
from time import sleep

config = Configurations()


if __name__ == "__main__":
    # MetroSpyder(config).run()

    while True:
        imovel = Imoveis(config).run()
        df = preprocess()
        sleep(1*60*60) # Buscar dados novos a cada uma hora

    # from aluguel.fetcher.aux import *
    # from selenium.webdriver import Chrome
    # from selenium.webdriver.common.keys import Keys
    # from selenium.webdriver.common.by import By
    # from math import ceil

    # url = "https://www.zapimoveis.com.br"
    # driver = Chrome(config["dir_webdriver"])
    # driver.maximize_window()
    # driver.get(url)

    # tipo_contrato = "Alugar"
    # tipo_propriedade = "Apartamento"
    # local = "Tijuca"
    # valor_minimo = 100
    # valor_maximo = 1000
    # max_page = 10
