import re
from retry import retry
from timeout_decorator import timeout


@retry(delay=3)
@timeout(5)
def get_with_retry(driver, url):
    driver.get(url)


def get(r, xpath, to_int=False):
    return parse_int(r.xpath(xpath).get(), to_int)


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
