import argparse
from fetcher.imoveis import Imoveis
from fetcher.metro import MetroSpyder
from data.preprocess import preprocess
from config import Configurations

config = Configurations()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "--site", choices=["zap", "vivareal"], default=["zap", "vivareal"], nargs="+",
    )
    p.add_argument("--max_page", default="5")
    p.add_argument("--tipo_contrato", choices=["aluguel"], default="aluguel")
    p.add_argument("--tipo_propriedade", choices=["apartamento"], default="apartamento")
    p.add_argument("--uf", choices=["rj"], default="rj")
    p.add_argument("--cidade", choices=["rio de janeiro"], default="rio de janeiro")
    p.add_argument("--zona", choices=["zona norte"], default="zona norte")
    p.add_argument("--bairro", choices=["tijuca"], default="tijuca")
    p.add_argument("--teste", action="store_true")

    arguments = vars(p.parse_args())

    # MetroSpyder().run()

    imovel = Imoveis(conf=config, **arguments)
    # imovel.run()

    # df = preprocess()

    # url = "https://www.vivareal.com.br/imovel/apartamento-2-quartos-tijuca-zona-norte-rio-de-janeiro-com-garagem-70m2-aluguel-RS1800-id-2488583906/"
    # print(imovel.parse_imovel(url, mode="r"))

    # url = "https://www.zapimoveis.com.br/imovel/aluguel-apartamento-3-quartos-tijuca-zona-norte-rio-de-janeiro-rj-80m2-id-2489499496/"
    # print(imovel.parse_imovel(url, mode="r"))
    
    # from selenium.webdriver.common.by import By
    # from selenium.webdriver import Chrome

    # url = "https://www.vivareal.com.br/"
    # driver = Chrome(config["dir_webdriver"])
    # driver.maximize_window()
    # driver.get(url)

    # t = driver.find_elements(By.XPATH, '//select[@class="js-select-business"]/option')

    # f = [t[i] for i, a in enumerate(t) if a.get_attribute("text") == "Alugar"]

    # f[0].click()
    

    # find = driver.find_elements(By.XPATH, '//input[@id="filter-location-search-input"]')[0]
    # find.send_keys('tijuca')
    # driver.find_elements(By.XPATH, '//div[@class="location-suggestions__container js-autocomplete"]/ul/li')[0].click()



    # id_ = re.findall("(id)-(\d{5,10})", url)[0][1]

    # tipo = get(driver, '//*[@class="price__title"]') or get(
    #     driver, '//*[@class="info__business-type color-dark text-regular"]'
    # )

    # title = get(driver, '//*[@class="title__title js-title-view"]') or get(
    #     driver,
    #     '//*[@class="main__info--title heading-large heading-large__bold align-left"]',
    # )

    # endereco = get(driver, '//*[@class="title__address js-address"]') or get(
    #     driver, "//article[1]/div/div[1]/div[1]/p/button/span[2]",
    # )

    # metragem = get(
    #     driver, '//*[@class="features__item features__item--area js-area"]', True,
    # ) or get(driver, '//*[@class="feature__item text-regular js-areas"]', True)

    # quartos = get(
    #     driver,
    #     '//*[@class="features__item features__item--bedroom js-bedrooms"]',
    #     True,
    # ) or get(driver, '//*[@class="feature__item text-regular js-bedrooms"]', True)

    # banheiros = get(
    #     driver,
    #     '//*[@class="features__item features__item--bathroom js-bathrooms"]/span',
    #     True,
    # ) or get(driver, '//*[@class="feature__item text-regular js-bathrooms"]', True,)

    # vagas = get(
    #     driver, '//*[@class="features__item features__item--parking js-parking"]', True,
    # ) or get(
    #     driver, '//*[@class="feature__item text-regular js-parking-spaces"]', True,
    # )

    # desc = driver.find_elements(
    #     By.XPATH, '//*[@class="description__text"]'
    # ) or driver.find_elements(
    #     By.XPATH, '//*[@class="amenities__description text-regular text-margin-zero"]',
    # )

    # desc = " ".join([d.text for d in desc])

    # preco = get(
    #     driver, '//*[@class="price__price-info js-price-sale"][last()]', True,
    # ) or get(
    #     driver,
    #     '//*[@class="price__item--main text-regular text-regular__bolder"][last()]',
    #     True,
    # )

    # condominio = get(
    #     driver, '//*[@class="price__list-value condominium js-condominium"]', True,
    # ) or get(
    #     driver, '//*[@class="price__item condominium color-dark text-regular"]', True,
    # )

    # imagens = driver.find_elements(
    #     By.XPATH, '//li[@class="carousel__slide js-carousel-item-wrapper"]/img',
    # ) or driver.find_elements(
    #     By.XPATH, '//li[@class="js-carousel-item carousel__item"]/img',
    # )

    # imagens = [img.get_attribute("src") for img in imagens]

    # sucesso, click, tentativa = False, False, 1
    # message, glink, lat, lng = "", "", "", ""

    # botao_xpath = [
    #     '//div[@class="box--display-flex box--items-baseline"]//button',
    #     '//button[@class="map__navigate js-navigate"]',
    # ]
    # glink_iframe_xpath = [
    #     '//*[@id="listing-map"]/article/iframe',
    #     '//*[@id="js-site-main"]//iframe',
    # ]
    # glink_xpath = [
    #     '//*[@id="mapDiv"]/div/div/div[8]/div/div/div/div[7]/div/a[contains(@href,"")]',
    #     '//*[@id="mapDiv"]//div[@class="google-maps-link"]/a[contains(@href,"")]'
    # ]
    # botao_fotos_xpath = "//li[1]/button"

    # try:
    #     botao = get_if_exists(driver, botao_xpath[0]) or get_if_exists(
    #         driver, botao_xpath[1]
    #     )
    #     if botao:
    #         botao.click()
    #         sleep(2)
    # except:
    #     pass

    # iframe = get_if_exists(driver, glink_iframe_xpath[0]) or get_if_exists(
    #     driver, glink_iframe_xpath[1]
    # )
    # if iframe:
    #     driver.switch_to.frame(iframe)
    #     sleep(3)
    #     glink = get_if_exists(driver, glink_xpath[0]) or get_if_exists(
    #         driver, glink_xpath[1]
    #     )

    #     if glink:
    #         glink = glink.get_attribute("href")
    #         latlng = re.findall("(.\d{2}\.\d{4,6})", glink)
    #         if len(latlng) >= 2:
    #             lat, lng = float(latlng[0]), float(latlng[1])
    #             sucesso = True

    #     driver.switch_to.default_content()

    # if not sucesso:
    #     sleep(1)
    #     tentativa += 1



