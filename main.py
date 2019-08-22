# Цель проекта, спасти мою безработную жизнь :3
__author__ = 'https://t.me/moonZlo'

import pickle
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from contextlib import contextmanager
import time

EMAIL = ''
PASSWORD = ''


def get_authorization_data(autch_patch: str):
    # data format email:password
    with open(autch_patch, 'r') as file:
        data = file.readline()
        value = data.split(':')

    global EMAIL
    global PASSWORD

    EMAIL = value[0]
    PASSWORD = value[1]


def safety_get(driver: webdriver.Chrome, url: str):
    driver.set_page_load_timeout(7)
    try:
        driver.get(url)

    except TimeoutException:
        print('page refresh')
        driver.refresh()


@contextmanager
def selen(driver_patch: str, profile_patch: str, config='windows') -> webdriver.Chrome:
    """
    Самый удобный метод использования веб драйвера =)
    :param driver_patch: str: patch to chromedriver(exe)
    :param profile_patch: str: the path to the folder storing cookies
    :param config: str: operating system
    :return: webdriver.Chrome
    """

    def windows_conf():
        return webdriver.Chrome(executable_path=driver_patch)

    def linux_conf():
        options = webdriver.ChromeOptions()
        arguments = ('headless', '--no-sandbox', '--disable-dev-shm-usage', f'user-data-dir={profile_patch}')
        for option in arguments:
            options.add_argument(option)

        driver = webdriver.Chrome(executable_path=driver_patch, chrome_options=options)
        return driver

    configs = {'windows': windows_conf, 'linux': linux_conf}
    web_driver = configs.get(config)()

    try:
        yield web_driver
        web_driver.close()
        time.sleep(1)
        web_driver.quit()

    except Exception as error:
        web_driver.close()
        time.sleep(1)
        web_driver.quit()
        raise Exception(error)


def hh_login(driver: webdriver.Chrome, email: str, password: str, cookies_patch: str) -> bool:
    safety_get(driver, 'https://hh.ru/account/login')
    finder = driver.find_element_by_xpath

    def login():
        finder('//input[@type="email"]').send_keys(email)
        time.sleep(2)
        finder('//input[@type="password"]').send_keys(password)
        time.sleep(2)
        finder('//input[@type="submit"]').click()
        time.sleep(2)

        safety_get(driver, 'https://hh.ru/applicant/settings?from=header_new')

        try:
            finder('//button[@data-qa="mainmenu_applicantProfile "]')
            pickle.dump(driver.get_cookies(), open(cookies_patch, "wb"))
            print('new cookies saved')
            return True

        except NoSuchElementException:
            raise Exception('authorization failed')

    try:
        # check authorization
        finder('//button[@data-qa="mainmenu_applicantProfile "]')
        print('authorization has been made')
        return True

    except NoSuchElementException:
        return login()


def hh_start(driver: webdriver.Chrome, cookies_patch: str) -> bool:
    """
    Применение куков, если они не валидные то получаем новые.

    """
    def set_cookie() -> bool:
        try:
            cookies = pickle.load(open(cookies_patch, "rb"))
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                driver.add_cookie(cookie)
            return True

        except FileNotFoundError:
            return False

    safety_get(driver, 'https://hh.ru/account/login')

    finder = driver.find_element_by_xpath
    set_cookie()

    # refresh
    driver.refresh()
    time.sleep(3)

    try:
        # check authorization
        finder('//button[@data-qa="mainmenu_applicantProfile "]')
        return True

    except NoSuchElementException:
        hh_login(driver, EMAIL, PASSWORD, cookies_patch)
        if set_cookie():
            return True

        else:
            raise Exception('Cookie set error')


def hh_update(driver: webdriver.Chrome, resume_title: str):
    """
    Производит нажатие кнопки 'Обновить резюме'

    """
    def find_resume(div_list: list) -> webdriver.remote:
        # Поиск конкретного резюме, требущие обновления.
        for res in div_list:
            try:
                data = res.find_element_by_xpath(f'.//h3').text
                if data == resume_title:
                    return res

            except NoSuchElementException:
                continue

        raise Exception('Resume title not found')

    safety_get(driver, 'https://m.hh.ru/applicant/resumes')
    time.sleep(2)

    all_resume = driver.find_elements_by_xpath('//li[@class="resume-list-item"]')

    my_resume = find_resume(all_resume)

    update_button = my_resume.find_element_by_xpath('.//button')
    if 'round-button_disabled'not in update_button.get_attribute('class'):
        update_button.click()
        time.sleep(2)
        return True

    else:
        print('Not updated')
        return False


def search_and_response(driver: webdriver.Chrome, resume_title: str, keyword: list):
    # coming soon
    pass


def main():
    chrome_driver = r'C:\chromedriver.exe'
    profile_patch = r'C:\profile'
    cookie_patch = 'cookies.pkl'
    authorization_patch = 'login.txt'

    with selen(chrome_driver, profile_patch) as driver:
        get_authorization_data(authorization_patch)
        if hh_start(driver, cookie_patch):
            hh_update(driver, 'Resume title')
            return True

        else:
            raise Exception('hh_start error')


if __name__ == '__main__':
    main()
