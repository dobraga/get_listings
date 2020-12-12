import re
from retry import retry
from timeout_decorator import timeout


@retry(tries=10, logger=None)
@timeout(5)
def get_with_retry(driver, url):
    driver.get(url)


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
    return list(set(sum(input, [])))
