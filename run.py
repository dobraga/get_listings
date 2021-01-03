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
        r = requests.get("https://github.com/aerokube/cm/releases/download/1.7.2/cm_linux_amd64")
        with open("cm", "wb") as file:
            file.write(r.content)
        os.system("chmod +x cm")

    os.system("./cm selenoid start")
    os.system("./cm selenoid-ui start")

    MetroSpyder(conf).run()
    imovel = Imoveis(conf)

    try:
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
