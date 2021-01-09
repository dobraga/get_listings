if __name__ == "__main__":
    from aluguel.data.preprocess import preprocess
    from aluguel.fetcher.metro import MetroSpyder
    from aluguel.fetcher.imoveis import Imoveis
    from aluguel.config import Configurations
    from aluguel.config.log import Logger
    from aluguel import Selenoid, timeit
    from time import sleep
    
    log = Logger("aluguel")
    conf = Configurations()


    try:
        with Selenoid(log):
            # MetroSpyder(conf).run()
            imovel = Imoveis(conf, log)

            while True:
                with timeit(log, "Processo finalizado em {delta} segundos"):
                    imovel.run()
                    preprocess()
                    sleep(1*60*60) # Buscar dados novos a cada uma hora

    except KeyboardInterrupt:
        log.warning("Processo cancelado\n")

    except Exception as e:
        log.error(f"Proceso finalizado com erro: {str(e)}\n")

