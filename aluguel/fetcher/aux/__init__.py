from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from timeout_decorator import timeout
from retry import retry
from time import sleep
import re

@retry(tries=10, logger=None)
@timeout(30)
def get_sleep(driver, url, time_sleep=8, time_sleep_ini=0):
    sleep(time_sleep_ini)
    driver.get(url)
    sleep(time_sleep)


def get(driver, xpath, to_int=False):
    element = get_if_exists(driver, xpath)
    if element:
        return parse_int(element.text, to_int)
    else:
        return None


def get_if_exists(driver, xpath):
    if driver.find_elements_by_xpath(xpath):
        return driver.find_element_by_xpath(xpath)
    else:
        return None


def parse_int(s, to_int=False):
    try:
        s = s.strip()
        if to_int:
            s = "".join(re.findall("[0-9|\,]", s))
            s = s.replace(",", ".")
            return int(s)
        else:
            return s
    except:
        if to_int:
            return 0
        else:
            return ""


def flat(input: list):
    """
    Transforma lista de listas em uma lista e remove duplicadas
    """
    output = []
    for l in input:
        if isinstance(l, list):
            output += l
        else:
            output.append(l)

    return output

def str_flat(str: str):
    return ''.join(str.split())

def pass_cookie(driver):
    try:
        iframe_xpath = '//iframe[@name="mtm-frame-prompt"]'
        iframe = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, iframe_xpath))
        )

        driver.switch_to.frame(iframe)
        get_if_exists(
            driver, '//button[text()="Sim"]'
        ).click()
    except:
        pass
    finally:
        driver.switch_to.default_content()

