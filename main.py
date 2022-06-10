import os
import sys
from pathlib import Path
from random import choice

import schedule
from dotenv import load_dotenv
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from MessagePack import print_exception_msg, print_info_msg
from ProjectSetup.setup import ProjSetup
from chromedriver_patch import download_latest_chromedriver
from g_spreadsheets import add_spreadsheet_data, clear_spreadsheet

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
setup = ProjSetup(BASE_DIR)
WINDOW_SIZE = "1920,1080"
CHROMEDRIVER_PATH = os.path.normpath(os.path.join(os.getcwd(), 'chromedriver', "chromedriver.exe")) \
    if setup.DEV else '/usr/local/bin/chromedriver'
SPREADSHEET_ID = '1gx_dCPMI_2ygTqxcnMMY_MGnSEjcDerwaFOqPTYlbgI'
HEADER = ['Квартира', 'Статус', 'Цена']

user_agents = None


def try_func(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # print_exception_msg(msg=f'@try_func - some error')
            err_log(str(e))
    return wrapper


def err_log(msg):
    f = open("error.log", "a")
    f.write(msg + '\n')
    f.close()


def get_driver():
    driver = None
    for i in range(10):
        try:
            service = Service(CHROMEDRIVER_PATH)
            # service.creationflags = CREATE_NO_WINDOW
            u_agent = get_user_agent()
            options = webdriver.ChromeOptions()
            options.add_argument('user-agent=' + u_agent)
            options.add_argument('headless')
            options.add_argument("--window-size=%s" % WINDOW_SIZE)
            options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            # print_exception_msg(str(e))
            if setup.DEV:
                check_chromedriver(driver)
            else:
                return None


def check_chromedriver(driver):
    if not os.path.exists('C:/Program Files/Google/Chrome/Application/chrome.exe'):
        sys.exit(
            "[ERR] Please make sure Chrome browser is installed "
            "(path is exists: C:/Program Files/Google/Chrome/Application/chrome.exe) "
            "and updated and rerun program"
        )
    # download latest chromedriver, please ensure that your chrome is up to date
    if driver is None:
        is_patched = download_latest_chromedriver()
    else:
        is_patched = download_latest_chromedriver(
            driver.capabilities["version"]
        )
    if not is_patched:
        sys.exit(
            "[ERR] Please update the chromedriver.exe in the webdriver folder "
            "according to your chrome version: https://chromedriver.chromium.org/downloads"
        )


def get_user_agent():
    global user_agents
    if user_agents is None:
        user_agents = open('text_files/user_agents.txt').read().strip().split('\n')
        for ua in user_agents:
            if len(ua) == 0:
                user_agents.remove(ua)
        # print_info_msg(f' user agent list count: {len(user_agents)}')
    return choice(user_agents) if len(user_agents) > 0 else None


def pars_data():
    driver = get_driver()
    if driver is None:
        # print_info_msg('Failed to get webdriver instance, check Chrome installation and version.')
        return None
    driver.get('https://brusnika-dom.ru/выбор-квартир-таблица/')
    while True:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, '#wpt_table > tbody > tr')
            el = els[-1].find_element(By.CSS_SELECTOR, 'td:nth-child(2) a').text
            if 'Квартира' not in el:
                break
            bt = driver.find_element(By.CSS_SELECTOR, '#wpt_load_more_wrapper_1800 > button')
            bt.click()
            sleep(3)
        except Exception as e:
            # print_exception_msg(str(e))
            pass
    # print_info_msg(f'els: {len(els)}')
    data = []
    for el in els:
        row = []
        # квартира, дом
        try:
            el_ = el.find_element(By.CSS_SELECTOR, 'td:nth-child(2) a').text
            row.append(el_)
            if 'Квартира' not in el_:
                print('data count:', len(data))
                return data
        except Exception as e:
            # print_exception_msg(str(e))
            row.append('')
        # статус
        try:
            el_ = el.find_element(By.CSS_SELECTOR, 'td:nth-child(3) div p').text
            row.append(el_)
        except Exception as e:
            # print_exception_msg(str(e))
            row.append('')
        # цена
        try:
            el_ = el.find_element(By.CSS_SELECTOR, 'td:nth-child(4) div').text
            row.append(el_)
        except Exception as e:
            # print_exception_msg(str(e))
            row.append('')
        print(row)
        data.append(row)
    return data


@try_func
def check_table_data():
    data_ = pars_data()
    if data_ and len(data_) > 0:
        clear_spreadsheet(SPREADSHEET_ID)
        add_spreadsheet_data(data_, SPREADSHEET_ID, HEADER)


if __name__ == "__main__":
    check_table_data()
    schedule.every(10).minutes.do(check_table_data)
    while True:
        schedule.run_pending()
        sleep(1)
