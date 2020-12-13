from fetcher.imoveis import Imoveis
from fetcher.metro import MetroSpyder
from data.preprocess import preprocess
from config import Configurations

config = Configurations()


if __name__ == "__main__":
    # MetroSpyder(config).run()

    imovel = Imoveis(config)
    imovel.run()

    # df = preprocess()


    # from aluguel.fetcher.aux import *
    # from selenium.webdriver import Chrome

    # driver = Chrome(config["dir_webdriver"])
    # driver.maximize_window()
    # url = "https://www.imovelweb.com.br/"
    # driver.get(url)

    # tipo_contrato = "Alugar"
    # tipo_propriedade = "Casa"
    # local = "Tijuca"



