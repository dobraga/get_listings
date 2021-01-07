if __name__ == "__main__":
    from aluguel.data.preprocess import preprocess
    from aluguel.fetcher.metro import MetroSpyder
    from aluguel.fetcher.imoveis import Imoveis
    from aluguel.config import Configurations
    from aluguel.config.log import Logger
    from time import sleep, time
    import requests
    import os

    log = Logger("aluguel")
    conf = Configurations()

    if not os.path.exists("cm"):
        log.info("Baixando Selenoid ...")
        r = requests.get("https://github.com/aerokube/cm/releases/download/1.7.2/cm_linux_amd64")
        with open("cm", "wb") as file:
            file.write(r.content)
        os.system("chmod +x cm")
        log.info("Selenoid baixado com sucesso")
    else:
        log.info("Selenoid já existente")

    os.system("./cm selenoid start")
    os.system("./cm selenoid-ui start")
    log.info("Selenoid iniciou com sucesso")

    try:
        # MetroSpyder(conf).run()
        imovel = Imoveis(conf, log)

        while True:
            ini = time()
            log.info("Processo iniciou")
            imovel.run()
            preprocess()
            fim = time()
            log.info(f"Processo finalizado em {fim - ini} segundos")
            sleep(1*60*60) # Buscar dados novos a cada uma hora

    except KeyboardInterrupt:
        log.warning("Processo cancelado")

    except Exception as e:
        log.error(f"Proceso finalizado com erro: {str(e)}")

    finally:
        os.system("./cm selenoid-ui stop")
        os.system("./cm selenoid stop")
        log.info("Selenoid parou com sucesso\n")
