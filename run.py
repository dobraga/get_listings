if __name__ == "__main__":
    from aluguel.data.preprocess import preprocess
    from aluguel.fetcher.metro import MetroSpyder
    from aluguel.fetcher.imoveis import Imoveis
    from aluguel.config import Configurations
    from time import sleep, time
    import requests
    import os

    conf = Configurations()

    if not os.path.exists("cm"):
        r = requests.get('https://github.com/aerokube/cm/releases/download/1.7.2/cm_linux_amd64')
        with open("cm", "wb") as file:
            file.write(r.content)
        os.system("chmod +x cm")

    os.system("./cm selenoid start")
    os.system("./cm selenoid-ui start")

    try:
        # MetroSpyder(conf).run()
        imovel = Imoveis(conf)

        while True:
            ini = time()
            imovel.run()
            preprocess()
            print("Terminou em ", time() - ini)
            sleep(1*60*60) # Buscar dados novos a cada uma hora

    except KeyboardInterrupt:
        print("Cancelado")

    except Exception as e:
        print(str(e))

    finally:
        os.system("./cm selenoid-ui stop")
        os.system("./cm selenoid stop")

    # from aluguel.fetcher.aux import *
    # from concurrent.futures import ProcessPoolExecutor
    # from selenium.webdriver.support import expected_conditions as EC
    # from selenium.webdriver.support.wait import WebDriverWait
    # from selenium.webdriver.common.keys import Keys
    # from selenium.webdriver.common.by import By
    # from selenium.webdriver import Remote
    # from os.path import join, exists
    # from retry import retry
    # from time import sleep
    # from math import ceil
    # import pandas as pd

    # driver = Remote(**conf["webdriver"])
    # url = "https://www.zapimoveis.com.br/imovel/aluguel-apartamento-2-quartos-com-elevador-tijuca-zona-norte-rio-de-janeiro-rj-73m2-id-2504093904/"
    # print(imovel.parse_imovel(url))

    # driver = Remote(desired_capabilities=options.to_capabilities())
    # url = "https://www.zapimoveis.com.br"
    # driver.get(url)
    
    
    # driver.close()

    # tipo_contrato = "Alugar"
    # tipo_propriedade = "Apartamento"
    # local = "Tijuca"
    # valor_minimo = 100
    # valor_maximo = 1000
    # max_page = 10
